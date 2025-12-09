from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QComboBox,
    QListView,
    QSizePolicy,
)
from PyQt5.QtCore import Qt
from configs import colors


class DarkListView(QListView):
    """
    Custom ListView to disable Ubuntu dimming effect.
    """

    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.Popup | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.setStyleSheet("background: transparent;")


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
            """
        )
        layout.addWidget(self.label)

        # ComboBox
        self.combo = QComboBox()
        self.combo.addItems(items)
        self.combo.setMinimumHeight(40)
        self.combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # -----------------------------
        # 🔥 FIX UTAMA: Non-Dimming Popup
        # -----------------------------
        popup = DarkListView()
        self.combo.setView(popup)

        # Custom dark popup style
        popup.setStyleSheet(
            f"""
            QListView {{
                background-color: {colors.SURFACE_COLOR};
                border: 1px solid {colors.BORDER_COLOR};
                padding: 6px;
                outline: none;
            }}
            QListView::item {{
                padding: 8px 12px;
                color: {colors.TEXT_PRIMARY};
            }}
            QListView::item:selected {{
                background-color: {colors.PRIMARY_COLOR};
                color: {colors.WHITE};
            }}
        """
        )

        # ComboBox style
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
            }}

            QComboBox:focus {{
                border: 1.5px solid {colors.PRIMARY_COLOR};
                background-color: {colors.SURFACE_COLOR};
            }}

            QComboBox::drop-down {{
                width: 28px;
                border: none;
                background: transparent;
            }}
        """
        )

        layout.addWidget(self.combo)

    def get_value(self):
        return self.combo.currentText()

    def set_value(self, value):
        index = self.combo.findText(value)
        if index >= 0:
            self.combo.setCurrentIndex(index)

    def set_items(self, items: list):
        self.combo.clear()
        self.combo.addItems(items)
