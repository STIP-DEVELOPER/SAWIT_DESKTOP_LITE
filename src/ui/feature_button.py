from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from utils.icon import get_icon


class FeatureButton(QPushButton):
    def __init__(self, text, icon_path=None):
        super().__init__(text)
        self.setFixedHeight(50)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(
            """
            QPushButton {
                background: #1e1b4b; color: #e0d4ff;
                border: 1px solid #5b21b6; border-radius: 16px;
                padding: 0 26px; font-size: 14px; font-weight: 600;
            }
            QPushButton:hover { background: #3a1b8a; border-color: #9d4edd; }
            QPushButton:pressed { background: #5b21b6; }
        """
        )
        if icon_path:
            self.setIcon(QIcon(get_icon(icon_path)))
