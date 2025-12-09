import os
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage
import cv2
from ultralytics import YOLO

from configs.config_manager import ConfigManager
from controller.serial import SerialController
from utils.path import ROOT_DIR


class YOLOThreadController(QThread):
    frame_ready = pyqtSignal(QImage)
    detection_ready = pyqtSignal(str)

    def __init__(self, lidar_left, lidar_right):
        super().__init__()
        self.running = False
        self.cap = None
        self.left_distance = None
        self.right_distance = None

        self._init_configs()
        self._init_serial_controller()

        self.lidar_left = lidar_left
        self.lidar_right = lidar_right

        self.lidar_left.data_received.connect(self.update_left_distance)
        self.lidar_right.data_received.connect(self.update_right_distance)

    def _init_configs(self):
        self.config_manager = ConfigManager()
        self.configs = self.config_manager.get_all()

        self.camera_index = self.configs.get("CAMERA_INDEX", 0)
        self.model_name = self.configs.get("YOLO_MODEL", "medium_tree")
        self.conf_threshold = self.configs.get("CONFIDENCE", 0.6)
        self.serial_port = self.configs.get("SERIAL_PORT", "")
        self.baudrate = self.configs.get("BAUDRATE", 9600)
        self.frame_skip = self.configs.get("FPS", 5)
        self.lidar_threshold = self.configs.get("LIDAR_THRESHOLD", 200)

        self.counter = 0
        self.model = YOLO(self._get_model_path(self.model_name))

    def _get_model_path(self, model_name):
        MODEL_PATH = os.path.join(ROOT_DIR, "models", model_name)

        print(f"[YOLOThread] Model path: {MODEL_PATH}")
        return MODEL_PATH

    def _init_serial_controller(self):
        if self.serial_port:
            self.serial_controller = SerialController(
                port=self.serial_port, baudrate=self.baudrate
            )
            self.serial_controller.start()
        else:
            self.serial_controller = None

    def update_left_distance(self, data):
        self.left_distance = data["distance_cm"]

    def update_right_distance(self, data):
        self.right_distance = data["distance_cm"]

    def _is_distance_valid(self, position):
        print(f"[YOLOThread] Checking distance for position: {position}")
        # MIN_THRESHOLD = 10  # minimum 10 cm

        # if position == "LEFT":
        #     print(f"======LEFT: {self.left_distance}cm")
        #     print(f"======[YOLOThrede] : min threshold {MIN_THRESHOLD}")
        #     print(f"======[YOLOThrede] : max threshold {self.lidar_threshold}")
        #     return (
        #         self.left_distance is not None
        #         and MIN_THRESHOLD < self.left_distance < self.lidar_threshold
        #     )

        # elif position == "RIGHT":
        #     print(f"======LEFT: {self.left_distance}cm")
        #     print(f"======[YOLOThrede] : min threshold {MIN_THRESHOLD}")
        #     print(f"======[YOLOThrede] : max threshold {self.lidar_threshold}")
        #     return (
        #         self.right_distance is not None
        #         and MIN_THRESHOLD < self.right_distance < self.lidar_threshold
        #     )

        return True

    def get_object_position(self, frame_width, box):
        x1, y1, x2, y2 = box.xyxy[0]
        x_center = (x1 + x2) / 2
        half_width = frame_width / 2

        return "LEFT" if x_center < half_width else "RIGHT"

    def _send_serial_message(self, message):
        if (
            self.serial_controller
            and self.serial_controller.ser
            and self.serial_controller.ser.is_open
        ):
            if self.serial_controller.is_busy:
                print("[YOLOThread] Arduino is BUSY → Skip sending")
                self.detection_ready.emit("[YOLOThread] Arduino is BUSY → Skip sending")
                return

            self.serial_controller.send(message)

    def setup(self):
        inferance_type = "webcam"
        source = (
            self.camera_index
            if inferance_type == "webcam"
            else "videos/sample-small-v1.mp4"
        )

        self.cap = cv2.VideoCapture(source)

        if not self.cap.isOpened():
            raise RuntimeError(f"Failed to open camera at index {self.camera_index}")

        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    def run(self):
        self.running = True
        last_annotated = None

        while self.running:
            if self.cap is None:
                break

            ret, frame = self.cap.read()

            if not ret or frame is None:
                QThread.msleep(10)
                continue

            else:
                self.counter += 1
                do_detect = self.counter % max(1, self.frame_skip) == 0

                if do_detect:
                    if not self.running:
                        break

                    results = self.model(
                        frame,
                        imgsz=640,
                        verbose=False,
                        conf=self.conf_threshold,
                    )

                    if not self.running:
                        break

                    annotated = results[0].plot()
                    last_annotated = annotated

                    if results[0].boxes is not None and len(results[0].boxes) > 0:
                        cls = int(results[0].boxes[0].cls)
                        name = results[0].names[cls]
                        conf = float(results[0].boxes[0].conf)
                        box = results[0].boxes[0]
                        position = self.get_object_position(frame.shape[1], box)

                        message = ""

                        if position == "LEFT":
                            message = (
                                f"Left |{name}| {conf:.2f}| {self.left_distance} cm"
                            )

                        if position == "RIGHT":
                            message = (
                                f"Right |{name}| {conf:.2f}| {self.right_distance} cm"
                            )

                        self.detection_ready.emit(message)

                        if self._is_distance_valid(position):
                            self._send_serial_message(position)
                else:
                    annotated = last_annotated if last_annotated is not None else frame

            if annotated is None or annotated.size == 0:
                continue

            rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
            h, w = rgb.shape[:2]

            if not self.running:
                break

            qt_image = QImage(rgb.data, w, h, w * 3, QImage.Format_RGB888).copy()

            if not self.running:
                break

            try:
                self.frame_ready.emit(qt_image)
            except RuntimeError:
                break

    def stop(self):
        print("[YOLOThread] Stop requested")

        self.running = False

        # Tunggu loop selesai
        if self.isRunning():
            self.wait()

        # Cleanup camera
        try:
            if self.cap is not None:
                self.cap.release()
        except Exception as e:
            print("[YOLOThread] cap release error:", e)

        self.cap = None

        if self.serial_controller:
            self.serial_controller.stop()
            self.serial_controller = None

        print("[YOLOThread] Fully stopped")
