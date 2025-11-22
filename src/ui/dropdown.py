from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QSizePolicy
from PyQt5.QtCore import Qt

from configs import colors


class Dropdown(QWidget):
    def __init__(self, label_text="", items=None, default=None):
        super().__init__()

        if items is None:
            items = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        # Label
        self.label = QLabel(label_text)
        self.label.setStyleSheet(
            f"""
                color: {colors.TEXT_PRIMARY};
                font-size: 13px;
                font-weight: 600;
                letter-spacing: 0.3px;
            """
        )
        layout.addWidget(self.label)

        # Dropdown
        self.combo = QComboBox()
        self.combo.addItems(items)
        self.combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.combo.setMinimumHeight(40)

        if default in items:
            self.combo.setCurrentText(default)

        # Modern Style
        self.combo.setStyleSheet(
            f"""
            QComboBox {{
                background-color: {colors.SURFACE_COLOR};
                color: {colors.TEXT_PRIMARY};
                border: 1px solid {colors.BORDER_COLOR};
                border-radius: 12px;
                padding: 10px 14px;
                font-size: 14px;
            }}

            QComboBox:hover {{
                border: 1px solid {colors.PRIMARY_COLOR};
                background-color: {colors.SURFACE_COLOR};
            }}

            QComboBox:focus {{
                border: 1.5px solid {colors.PRIMARY_COLOR};
                background-color: {colors.WHITE};
            }}

            /* Arrow Button */
            QComboBox::drop-down {{
                width: 32px;
                border: none;
                background: transparent;
            }}

            /* Dropdown List */
            QComboBox QAbstractItemView {{
                background: {colors.WHITE};
                border: 1px solid {colors.BORDER_COLOR};
                padding: 6px;
                outline: none;
                selection-background-color: {colors.PRIMARY_COLOR};
                selection-color: {colors.TEXT_ON_PRIMARY};
                font-size: 14px;
            }}

            /* Items */
            QComboBox QAbstractItemView::item {{
                padding: 6px 10px;
                border-radius: 6px;
                margin: 2px;
            }}
        """
        )

        layout.addWidget(self.combo)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def get_value(self):
        return self.combo.currentText()

    def set_items(self, items):
        self.combo.clear()
        self.combo.addItems(items)

    def set_value(self, value):
        index = self.combo.findText(value)
        if index >= 0:
            self.combo.setCurrentIndex(index)

    def on_change(self, callback):

        self.combo.currentTextChanged.connect(callback)
