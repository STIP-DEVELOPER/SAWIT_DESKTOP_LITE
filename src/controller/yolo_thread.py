from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage
import cv2

from configs.config_manager import ConfigManager
from controller.serial import SerialController
from controller.yolo_detector import YOLOWebcamDetectorController
from enums.log import LogLevel, LogSource
from utils.logger import add_log
from controller.tfluna import TFLunaController


class YOLOThreadController(QThread):
    frame_ready = pyqtSignal(QImage)
    detection_ready = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._init_configs()
        self._init_detector()
        self._init_serial_controller()
        self.is_running = False

        self.left_distance = None
        self.right_distance = None
        self.tfluna_threshold = 50

        self.tf_luna_left = TFLunaController(port="PORT_KIRI")
        self.tf_luna_right = TFLunaController(port="PORT_KANAN")

        self.tf_luna_left.data_received.connect(self.update_left_distance)
        self.tf_luna_right.data_received.connect(self.update_right_distance)

        self.tf_luna_left.start()
        self.tf_luna_right.start()

    def _init_configs(self):
        self.config_manager = ConfigManager()
        self.configs = self.config_manager.get_all()
        self.camera_index = self.configs.get("CAMERA_INDEX", 0)
        self.model_name = self.configs.get("YOLO_MODEL", "medium_tree")
        self.conf_threshold = self.configs.get("CONFIDENCE", 0.6)
        self.serial_port = self.configs.get("SERIAL_PORT", "")
        self.baudrate = self.configs.get("BAUDRATE", 9600)

    def _init_detector(self):
        model_path = self._get_model_path(self.model_name)

        self.detector = YOLOWebcamDetectorController(
            model_path=model_path,
            conf_threshold=self.conf_threshold,
        )

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

    def setup(self):
        """Setup webcam for YOLO detector"""
        self.detector.setup_webcam(
            camera_index=self.camera_index, inferance_type="video"
        )

    def run(self):
        self.is_running = True
        while self.is_running:
            frame = self.detector.get_latest_frame()
            if frame is None:
                continue

            try:
                results = self._perform_detection(frame)
                self._process_frame(frame, results)
            except Exception as e:
                self._handle_detection_error(e)

    def update_left_distance(self, data):
        self.left_distance = data["distance_cm"]

    def update_right_distance(self, data):
        self.right_distance = data["distance_cm"]

    def _perform_detection(self, frame):
        """Run YOLO detection on frame"""
        return self.detector.model(frame, conf=self.conf_threshold, verbose=False)

    def _process_frame(self, frame, results):
        """Process frame: emit image and detection messages"""
        self._emit_frame(frame, results)
        self._process_detections(frame, results)

    def _emit_frame(self, frame, results):
        annotated_frame = results[0].plot()
        qt_image = self._convert_to_qimage(annotated_frame)
        self.frame_ready.emit(qt_image)

    def _convert_to_qimage(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        return QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)

    def _process_detections(self, frame, results):
        frame_width = frame.shape[1]
        if not results[0].boxes:
            return

        for box in results[0].boxes:
            self._handle_single_detection(box, results[0].names, frame_width)

    def _handle_single_detection(self, box, class_names, frame_width):
        center_x, _, _ = self.detector.get_center_coordinates(box)
        class_name = class_names[int(box.cls)]
        confidence = float(box.conf)
        position = self.detector.get_position(center_x, frame_width)

        if self.left_distance and self.left_distance < 50:
            position = "RIGHT"
        elif self.right_distance and self.right_distance < 50:
            position = "LEFT"

        self._send_serial_message(position)
        self._emit_detection_message(class_name, position, confidence)

    def _emit_detection_message(self, class_name, position, confidence):
        msg = f"[{class_name}] {position} | Conf: {confidence:.2f}"
        self.detection_ready.emit(msg)

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

    def _handle_detection_error(self, error):
        err_msg = f"[ERROR] Detection failed: {str(error)}"
        self.detection_ready.emit(err_msg)
        add_log(LogLevel.ERROR.value, LogSource.UI_SETTINGS.value, err_msg)

    def stop(self):
        "Stop thread"
        self.is_running = False
        if self.isRunning():
            self.wait(1000)
        self.detector.cleanup()
