from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGridLayout,
    QLabel,
    QHBoxLayout,
    QMessageBox,
)

from configs.config_manager import ConfigManager
from enums.log import LogLevel, LogSource
from ui.button import Button
from ui.dropdown import Dropdown
from ui.input import InputForm
from utils.logger import add_log
from utils.serial import get_serial_ports
from utils.icon import get_icon


def detect_camera_indexes(max_test=5):
    import cv2

    indexes = []
    for i in range(max_test):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            indexes.append(str(i))
            cap.release()
    return indexes


class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()

        self.configs = ConfigManager()
        self._build_ui()
        self._load_settings()

    def _build_ui(self):
        layout = QVBoxLayout()
        grid = QGridLayout()
        grid.setSpacing(20)
        grid.setContentsMargins(20, 20, 20, 20)

        detected_cameras = detect_camera_indexes()

        if not detected_cameras:
            detected_cameras = ["0", "1"]  # fallback

        usb_ports = get_serial_ports()
        usb_ports.append("None")

        if not usb_ports:
            usb_ports = ["No ports detected"]

        self.select_camera = Dropdown(
            label_text="Camera Index",
            items=detected_cameras,
        )

        self.select_model = Dropdown(
            label_text="Select Model",
            items=[
                "small_tree",
                "medium_tree",
                "large_tree",
            ],
        )

        self.select_port = Dropdown(
            label_text="Serial Port",
            items=usb_ports,
        )

        self.select_baudrate = Dropdown(
            label_text="Baudrate",
            items=["9600", "19200", "38400", "57600", "115200"],
        )

        self.select_fps = Dropdown(
            label_text="FPS (Frame Rate)",
            items=["5", "10", "15", "20", "25", "30"],
        )

        self.confidence = InputForm(label="Confidence Score (0.1 - 0.9)")

        self.confidence = Dropdown(
            label_text="Confidence Score (0.5 - 0.8)",
            items=["0.5", "0.6", "0.7", "0.8"],
        )

        self.select_lidar_left = Dropdown(
            label_text="Lidar Left Port",
            items=usb_ports,
        )

        self.select_lidar_right = Dropdown(
            label_text="Lidar Right Port",
            items=usb_ports,
        )

        self.select_lidar_threshold = Dropdown(
            label_text="Lidar Threshold (cm)",
            items=["100", "150", "200", "250", "300", "350", "400", "500"],
        )

        # -------------------------
        # HEADER Camera
        # -------------------------
        camera_header = QLabel("Camera")
        camera_header.setStyleSheet("font-weight: bold; font-size: 14px;")
        grid.addWidget(camera_header, 0, 0, 1, 4, alignment=Qt.AlignLeft)

        # Row 1 → Camera Index + FPS
        grid.addWidget(QLabel("Camera Index:"), 1, 0, alignment=Qt.AlignRight)
        grid.addWidget(self.select_camera, 1, 1)

        grid.addWidget(QLabel("FPS:"), 1, 2, alignment=Qt.AlignRight)
        grid.addWidget(self.select_fps, 1, 3)

        # -------------------------
        # HEADER AI
        # -------------------------
        ai_header = QLabel("AI")
        ai_header.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 10px;")
        grid.addWidget(ai_header, 2, 0, 1, 4, alignment=Qt.AlignLeft)

        # Row 3 → Model + Confidence
        grid.addWidget(QLabel("Select Model:"), 3, 0, alignment=Qt.AlignRight)
        grid.addWidget(self.select_model, 3, 1)

        grid.addWidget(QLabel("Confidence:"), 3, 2, alignment=Qt.AlignRight)
        grid.addWidget(self.confidence, 3, 3)

        # -------------------------
        # HEADER Serial
        # -------------------------
        serial_header = QLabel("Serial")
        serial_header.setStyleSheet(
            "font-weight: bold; font-size: 14px; margin-top: 10px;"
        )
        grid.addWidget(serial_header, 4, 0, 1, 4, alignment=Qt.AlignLeft)

        # Row 5 → Serial Port + Baudrate
        grid.addWidget(QLabel("Serial Port:"), 5, 0, alignment=Qt.AlignRight)
        grid.addWidget(self.select_port, 5, 1)

        grid.addWidget(QLabel("Baudrate:"), 5, 2, alignment=Qt.AlignRight)
        grid.addWidget(self.select_baudrate, 5, 3)

        # LIDAR Header
        lidar_header = QLabel("Lidar")
        lidar_header.setStyleSheet(
            "font-weight: bold; font-size: 14px; margin-top: 10px;"
        )
        grid.addWidget(lidar_header, 6, 0, 1, 4)

        # LIDAR Left
        grid.addWidget(QLabel("Lidar Left Port:"), 7, 0, alignment=Qt.AlignRight)
        grid.addWidget(self.select_lidar_left, 7, 1)

        # LIDAR Right
        grid.addWidget(QLabel("Lidar Right Port:"), 7, 2, alignment=Qt.AlignRight)
        grid.addWidget(self.select_lidar_right, 7, 3)

        # LIDAR Threshold
        grid.addWidget(QLabel("Lidar Threshold:"), 8, 0, alignment=Qt.AlignRight)
        grid.addWidget(self.select_lidar_threshold, 8, 1)

        # Save Button
        self.save_button = Button(
            text="Save Settings",
            icon_path=get_icon("save.png"),
        )
        self.save_button.clicked.connect(self._save_settings)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        button_layout.setContentsMargins(0, 0, 20, 0)

        layout.addLayout(grid)
        layout.addLayout(button_layout)
        layout.addStretch()
        self.setLayout(layout)

    def _load_settings(self):
        cfg = self.configs.get_all()

        if "CAMERA_INDEX" in cfg:
            self.select_camera.set_value(str(cfg["CAMERA_INDEX"]))

        if "YOLO_MODEL" in cfg:
            self.select_model.set_value(cfg["YOLO_MODEL"])

        if "SERIAL_PORT" in cfg:
            self.select_port.set_value(cfg["SERIAL_PORT"])

        if "CONFIDENCE" in cfg:
            self.confidence.set_value(str(cfg["CONFIDENCE"]))

        if "BAUDRATE" in cfg:
            self.select_baudrate.set_value(str(cfg["BAUDRATE"]))

        if "FPS" in cfg:
            self.select_fps.set_value(str(cfg["FPS"]))

        if "LIDAR_LEFT_PORT" in cfg:
            self.select_lidar_left.set_value(cfg["LIDAR_LEFT_PORT"])

        if "LIDAR_RIGHT_PORT" in cfg:
            self.select_lidar_right.set_value(cfg["LIDAR_RIGHT_PORT"])

        if "LIDAR_THRESHOLD" in cfg:
            self.select_lidar_threshold.set_value(str(cfg["LIDAR_THRESHOLD"]))

    def _save_settings(self):
        try:
            camera_index = int(self.select_camera.get_value())
            model = self.select_model.get_value()
            serial_port = self.select_port.get_value()
            confidence = float(self.confidence.get_value())
            baudrate = int(self.select_baudrate.get_value())
            fps = int(self.select_fps.get_value())
            lidar_left_port = self.select_lidar_left.get_value()
            lidar_right_port = self.select_lidar_right.get_value()
            lidar_threshold = int(self.select_lidar_threshold.get_value())

            self.configs.set_config("CAMERA_INDEX", camera_index)
            self.configs.set_config("YOLO_MODEL", model)
            self.configs.set_config("SERIAL_PORT", serial_port)
            self.configs.set_config("CONFIDENCE", confidence)
            self.configs.set_config("BAUDRATE", baudrate)
            self.configs.set_config("FPS", fps)
            self.configs.set_config("LIDAR_LEFT_PORT", lidar_left_port)
            self.configs.set_config("LIDAR_RIGHT_PORT", lidar_right_port)
            self.configs.set_config("LIDAR_THRESHOLD", lidar_threshold)

            QMessageBox.information(self, "Successful", "Berhasil disimpan")

            add_log(
                LogLevel.INFO.value,
                LogSource.UI_SETTINGS.value,
                f"Settings saved {self.configs.get_all()}",
            )

        except ValueError:
            add_log(
                LogLevel.INFO.value,
                LogSource.UI_SETTINGS.value,
                f"Error: {self.configs.get_all()}",
            )
