from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


class ChatBubble(QWidget):
    def __init__(self, text: str, is_user: bool = False):
        super().__init__()
        hbox = QHBoxLayout(self)
        hbox.setContentsMargins(60, 12, 60, 12)

        label = QLabel(text)
        label.setWordWrap(True)
        label.setFont(QFont("SF Pro Display", 16))
        label.setContentsMargins(20, 16, 20, 16)

        if is_user:
            label.setStyleSheet(
                """
                background: #2d1b69; color: #e6d9ff;
                border-radius: 24px;
                border-bottom-left-radius: 8px;
                border: 1px solid #5b21b6;
            """
            )
            hbox.addWidget(label)
            hbox.addStretch()
        else:
            label.setStyleSheet(
                """
                background: #7c3aed; color: white;
                border-radius: 24px;
                border-bottom-right-radius: 8px;
            """
            )
            hbox.addStretch()
            hbox.addWidget(label)
