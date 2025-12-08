from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QTextEdit,
    QHBoxLayout,
    QSizePolicy,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

from configs.config_manager import ConfigManager
from controller.lidar import LidarController
from enums.log import LogLevel, LogSource
from ui.button import Button
from utils.format import format_log_text
from utils.icon import get_icon
from utils.logger import add_log
from controller.yolo import YOLOThreadController


class InferencePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.show_camera = True
        self.is_running = False
        self.yolo_thread = None
        self.original_frame_size = None
        self._build_ui()
        self._init_configs()

    def _init_configs(self):
        self.config_manager = ConfigManager()
        self.configs = self.config_manager.get_all()

        # self.lidar_left_port = self.configs.get("LIDAR_LEFT_PORT", "")
        # self.lidar_right_port = self.configs.get("LIDAR_RIGHT_PORT", "")

        self.lidar_left_port = "/dev/lidar_left"
        self.lidar_right_port = "/dev/lidar_right"

        self.lidar_left = LidarController(port=self.lidar_left_port)
        self.lidar_right = LidarController(port=self.lidar_right_port)

        self.lidar_left.start()
        self.lidar_right.start()

        print(f"[InferencePage] Lidar Left Port: {self.lidar_left_port}")
        print(f"[InferencePage] Lidar Right Port: {self.lidar_right_port}")

    def _build_ui(self):
        self.camera_container = QWidget(self)
        self.camera_container.setStyleSheet("background-color: transparent;")
        self.camera_container.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding
        )
        self.camera_container_layout = QVBoxLayout(self.camera_container)
        self.camera_container_layout.setContentsMargins(0, 0, 0, 0)
        self.camera_container_layout.setAlignment(Qt.AlignCenter)

        self.camera_label = QLabel()
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setMinimumSize(640, 480)
        self.camera_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.camera_label.setStyleSheet(self.camera_style())
        self.camera_label.setText("Camera feed will appear here")
        self.camera_container_layout.addWidget(self.camera_label)

        self.log_box = QTextEdit(self.camera_container)
        self.log_box.setReadOnly(True)
        self.log_box.setFixedWidth(300)
        self.log_box.setFixedHeight(150)
        self.log_box.setStyleSheet(self.log_style())

        self.start_button = Button(text="Start", icon_path=get_icon("start.png"))
        self.start_button.clicked.connect(self.toggle_start_stop)

        self.stop_button = Button(text="Stop", icon_path=get_icon("stop.png"))
        self.stop_button.clicked.connect(self.toggle_start_stop)
        self.stop_button.hide()

        self.toggle_camera_button = Button(
            text="Hide Camera", icon_path=get_icon("camera.png")
        )
        self.toggle_camera_button.clicked.connect(self.toggle_camera_visibility)

        control_layout = QHBoxLayout()
        control_layout.setSpacing(20)
        control_layout.setContentsMargins(0, 8, 0, 10)
        control_layout.setAlignment(Qt.AlignCenter)
        control_layout.addWidget(self.start_button)
        control_layout.addWidget(self.stop_button)
        control_layout.addWidget(self.toggle_camera_button)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.camera_container)
        main_layout.addLayout(control_layout)
        main_layout.setStretch(0, 1)  # Camera container gets most space
        main_layout.setStretch(1, 0)  # Controls get minimal space
        self.setLayout(main_layout)

    def toggle_start_stop(self):
        """Toggle inference start/stop state."""

        self.is_running = not self.is_running

        if self.is_running:
            self.start_button.hide()
            self.stop_button.show()
            self._append_log(
                format_log_text(
                    source=LogSource.UI_HOME.value,
                    message="Inference started...",
                )
            )
            add_log(LogLevel.INFO.value, LogSource.UI_HOME.value, "Inference started")

            self.start_yolo()
        else:
            self.stop_button.hide()
            self.start_button.show()

            self._append_log(
                format_log_text(
                    source=LogSource.UI_HOME.value,
                    message="Inference Stopped...",
                )
            )
            add_log(LogLevel.INFO.value, LogSource.UI_HOME.value, "Inference stopped")

            self.stop_yolo()

    def toggle_camera_visibility(self):
        """Toggle show/hide camera"""
        self.show_camera = not self.show_camera

        if self.show_camera:
            self.camera_label.show()
            self.toggle_camera_button.setText("Hide Camera")
            self._append_log(
                format_log_text(
                    source=LogSource.UI_HOME.value,
                    message="Camera shown",
                )
            )
            if (
                self.is_running
                and hasattr(self.camera_label, "pixmap")
                and self.camera_label.pixmap()
            ):
                pass
            else:
                self.camera_label.setText("Camera feed will appear here")
        else:
            self.last_pixmap = self.camera_label.pixmap()

            self.camera_label.clear()
            self.camera_label.setText(
                "Camera is currently hidden\nClick 'Show Camera' to view"
            )
            self.toggle_camera_button.setText("Show Camera")
            self._append_log(
                format_log_text(
                    source=LogSource.UI_HOME.value,
                    message="Camera hidden",
                )
            )

    def start_yolo(self):
        try:
            self._init_configs()
            self.yolo_thread = YOLOThreadController(
                lidar_left=self.lidar_left, lidar_right=self.lidar_right
            )

            if self.yolo_thread and self.yolo_thread.isRunning():
                self.yolo_thread.stop()
                self.yolo_thread.wait(3000)

            self.yolo_thread.frame_ready.connect(self.display_frame)
            self.yolo_thread.detection_ready.connect(self._append_log)

            self.yolo_thread.setup()
            self.yolo_thread.start()

            self._append_log("[INFO] Webcam initialized")

            if self.show_camera:
                self.camera_label.clear()

        except Exception as e:
            self._append_log(f"[ERROR] {str(e)}")
            self.camera_label.setText(f"Camera Error: {str(e)}")

    def stop_yolo(self):
        """Stop YOLO detection thread"""

        if self.yolo_thread and self.yolo_thread.isRunning():
            self.yolo_thread.stop()
            self.yolo_thread.wait(3000)
            self.yolo_thread = None
            self.original_frame_size = None

        if self.show_camera:
            self.camera_label.clear()
            self.camera_label.setText(
                "Camera stopped\nClick 'Start' to begin inference"
            )

    def display_frame(self, q_image):
        if not self.show_camera or not self.is_running:
            return

        pixmap = QPixmap.fromImage(q_image)

        if self.original_frame_size is None:
            self.original_frame_size = pixmap.size()

        scaled_pixmap = self.scale_pixmap_to_fit(pixmap)
        self.camera_label.setPixmap(scaled_pixmap)

    def scale_pixmap_to_fit(self, pixmap):
        container_size = self.camera_label.size()
        pixmap_size = pixmap.size()

        if container_size.width() <= 0 or container_size.height() <= 0:
            return pixmap

        if pixmap_size.width() <= 0 or pixmap_size.height() <= 0:
            return pixmap

        width_ratio = container_size.width() / pixmap_size.width()
        height_ratio = container_size.height() / pixmap_size.height()

        scale_ratio = min(width_ratio, height_ratio)

        new_width = int(pixmap_size.width() * scale_ratio)
        new_height = int(pixmap_size.height() * scale_ratio)

        return pixmap.scaled(
            new_width, new_height, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )

    def resizeEvent(self, event):
        super().resizeEvent(event)

        camera_rect = self.camera_container.rect()
        log_x = camera_rect.width() - self.log_box.width() - 20
        log_y = 20
        self.log_box.move(log_x, log_y)

        if (
            self.show_camera
            and self.is_running
            and hasattr(self.camera_label, "pixmap")
            and self.camera_label.pixmap()
        ):
            current_pixmap = self.camera_label.pixmap()
            scaled_pixmap = self.scale_pixmap_to_fit(current_pixmap)
            self.camera_label.setPixmap(scaled_pixmap)

    def _append_log(self, text: str):
        """Append message to overlay log box."""
        self.log_box.append(text)
        self.log_box.verticalScrollBar().setValue(
            self.log_box.verticalScrollBar().maximum()
        )

    def camera_style(self):
        return """
            QLabel {
                border: 2px solid #444;
                background-color: #111;
                color: #aaa;
                font-size: 14px;
                qproperty-alignment: AlignCenter;
            }
        """

    def log_style(self):
        return """
            QTextEdit {
                background-color: rgba(0, 0, 0, 150);
                color: #0f0;
                font-family: Consolas, monospace;
                font-size: 12px;
                border: 1px solid #333;
                border-radius: 6px;
                padding: 6px;
            }
        """

    def closeEvent(self, event):
        """Cleanup saat window ditutup"""
        if self.yolo_thread:
            self.stop_yolo()
        super().closeEvent(event)
