from PyQt5.QtWidgets import QPushButton
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import QSize, Qt
from configs import colors


class Button(QPushButton):
    def __init__(
        self,
        text="Button",
        icon_path=None,
        bg_color=colors.PRIMARY_COLOR,
        text_color=colors.TEXT_ON_PRIMARY,
        hover_color=colors.ACCENT_HOVER,
        radius=8,
        font_size=12,
        padding="8px 16px",
        parent=None,
    ):
        super().__init__(text, parent)

        if icon_path:
            self.setIcon(QIcon(icon_path))
            self.setIconSize(QSize(18, 18))

        self.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {bg_color};
                color: {text_color};
                border: none;
                border-radius: {radius}px;
                padding: {padding};
                font-size: {font_size}px;
                font-weight: 500;
                font-family: 'Segoe UI';
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            QPushButton:pressed {{
                background-color: #144a79;
            }}
        """
        )

        self.setCursor(Qt.PointingHandCursor)
        font = QFont()
        font.setPointSize(font_size)
        self.setFont(font)
