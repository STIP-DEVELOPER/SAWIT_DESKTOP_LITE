from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QGraphicsOpacityEffect
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation
from configs import colors


class Alert(QWidget):
    def __init__(self, parent, message, alert_type="info", duration=3000):
        super().__init__(parent)

        # ========= COLOR MAPPING =========
        type_color = {
            "success": colors.SUCCESS_COLOR,
            "error": colors.DANGER_COLOR,
            "warning": colors.WARNING_COLOR,
            "info": colors.INFO_COLOR,
        }

        bg = type_color.get(alert_type, colors.INFO_COLOR)

        # ========= BASE STYLE =========
        self.setStyleSheet(
            f"""
            background-color: {bg};
            color: {colors.TEXT_ON_PRIMARY};
            border-radius: 8px;
            padding: 10px 18px;
            font-size: 14px;
        """
        )
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.ToolTip)

        # ========= BODY =========
        layout = QHBoxLayout()
        layout.setContentsMargins(16, 10, 16, 10)
        layout.setSpacing(10)

        label = QLabel(message)
        label.setWordWrap(True)
        layout.addWidget(label)

        self.setLayout(layout)

        # ========= POSITION CENTER TOP =========
        self.adjustSize()
        parent_width = parent.width()

        self.move((parent_width - self.width()) // 2, 20)

        # ========= FADE IN =========
        self.opacity = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity)

        fade_in = QPropertyAnimation(self.opacity, b"opacity")
        fade_in.setDuration(250)
        fade_in.setStartValue(0)
        fade_in.setEndValue(1)
        fade_in.start()

        # ========= AUTO CLOSE =========
        QTimer.singleShot(duration, self.fade_out)

    def fade_out(self):
        fade = QPropertyAnimation(self.opacity, b"opacity")
        fade.setDuration(350)
        fade.setStartValue(1)
        fade.setEndValue(0)
        fade.finished.connect(self.close)
        fade.start()

    # ========= STATIC PUBLIC API =========
    @staticmethod
    def open(parent, message, alert_type="info", duration=3000):
        alert = Alert(parent, message, alert_type, duration)
        alert.show()
        return alert
