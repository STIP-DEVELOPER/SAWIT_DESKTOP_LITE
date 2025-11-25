from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage
import cv2
from ultralytics import YOLO

from configs.config_manager import ConfigManager
from controller.serial import SerialController
from controller.tfluna import TFLunaController


class YOLOThreadController(QThread):
    frame_ready = pyqtSignal(QImage)
    detection_ready = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.running = False
        self.cap = None

        self._init_configs()
        self._init_serial_controller()
        self._init_lidar_controller()

    def _init_configs(self):
        self.config_manager = ConfigManager()
        self.configs = self.config_manager.get_all()
        self.camera_index = self.configs.get("CAMERA_INDEX", 0)
        self.model_name = self.configs.get("YOLO_MODEL", "medium_tree")
        self.conf_threshold = self.configs.get("CONFIDENCE", 0.6)
        self.serial_port = self.configs.get("SERIAL_PORT", "")
        self.baudrate = self.configs.get("BAUDRATE", 9600)

        self.frame_skip = 5
        self.counter = 0

        self.model = YOLO(self._get_model_path(self.model_name))

    def _get_model_path(self, model_name):
        return f"models/{model_name}_ncnn_model"

    def _init_serial_controller(self):
        if self.serial_port:
            self.serial_controller = SerialController(
                port=self.serial_port, baudrate=self.baudrate
            )
            self.serial_controller.start()
        else:
            self.serial_controller = None

    def _init_lidar_controller(self):
        self.left_distance = None
        self.right_distance = None
        self.tfluna_threshold = 50

        self.tf_luna_left = TFLunaController(port="PORT_KIRI")
        self.tf_luna_right = TFLunaController(port="PORT_KANAN")

        self.tf_luna_left.data_received.connect(self.update_left_distance)
        self.tf_luna_right.data_received.connect(self.update_right_distance)

        self.tf_luna_left.start()
        self.tf_luna_right.start()

    def update_left_distance(self, data):
        self.left_distance = data["distance_cm"]

    def update_right_distance(self, data):
        self.right_distance = data["distance_cm"]

    def _is_distance_valid(self, position):
        threshold_cm = 200  # 2 meter

        if position == "LEFT":
            return self.left_distance is not None and self.left_distance < threshold_cm

        elif position == "RIGHT":
            return (
                self.right_distance is not None and self.right_distance < threshold_cm
            )

        return False

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
        inferance_type = "videos"
        source = (
            self.camera_index
            if inferance_type == "webcam"
            else "videos/sample-large-1.MOV"
        )

        self.cap = cv2.VideoCapture(source)
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    def run(self):
        self.running = True

        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                continue

            self.counter += 1
            do_detect = self.counter % self.frame_skip == 0

            if do_detect:
                results = self.model.predict(
                    frame,
                    verbose=False,
                    imgsz=640,
                    device="cpu",
                )
                annotated = results[0].plot()
            else:
                annotated = frame

            rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            qt_image = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
            self.frame_ready.emit(qt_image)

            if do_detect and results[0].boxes:
                cls = int(results[0].boxes[0].cls)
                name = results[0].names[cls]
                conf = float(results[0].boxes[0].conf)
                box = results[0].boxes[0]
                position = self.get_object_position(frame.shape[1], box)

                self.detection_ready.emit(f"{name} ({conf:.2f}) | {position}")

                if self._is_distance_valid(position):
                    self._send_serial_message(position)

    def stop(self):
        self.running = False
        if self.cap:
            self.cap.release()
        self.quit()
        self.wait(200)
