from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QIcon, QFont
from configs import colors


class InputForm(QWidget):
    text_changed = pyqtSignal(str)  # debounced output
    text_changed_raw = pyqtSignal(str)  # raw output

    def __init__(
        self,
        label: str = "",
        placeholder: str = "",
        default: str = "",
        password: bool = False,
        width: int = None,  # None = dynamic
        prefix_icon: str = None,  # path to icon
        suffix_icon: str = None,
        size: str = "md",  # sm | md | lg
        clearable: bool = True,
        disabled: bool = False,
        debounce: int = 150,  # ms
    ):
        super().__init__()

        self.label_text = label
        self.placeholder = placeholder
        self.default = default
        self.password = password
        self.width = width
        self.prefix_icon = prefix_icon
        self.suffix_icon = suffix_icon
        self.size_variant = size
        self.clearable = clearable
        self.disabled = disabled
        self.debounce = debounce

        self.debounce_timer = QTimer()
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.timeout.connect(self.emit_debounced)

        self.init_ui()

    # -------------------------------------------------------
    # UI Builder
    # -------------------------------------------------------

    def init_ui(self):
        root = QVBoxLayout()
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(4)

        # Label
        if self.label_text:
            label_widget = QLabel(self.label_text)
            label_widget.setStyleSheet(
                f"color: {colors.TEXT_PRIMARY}; font-size: 14px;"
            )
            root.addWidget(label_widget)

        # Input wrapper (prefix + input + suffix)
        wrap = QHBoxLayout()
        wrap.setContentsMargins(0, 0, 0, 0)
        wrap.setSpacing(4)

        # Prefix icon
        if self.prefix_icon:
            prefix_btn = QPushButton()
            prefix_btn.setIcon(QIcon(self.prefix_icon))
            prefix_btn.setStyleSheet("border: none; padding: 2px;")
            prefix_btn.setCursor(Qt.ArrowCursor)
            wrap.addWidget(prefix_btn)

        # QLineEdit
        self.input = QLineEdit()
        self.input.setPlaceholderText(self.placeholder)
        self.input.setText(self.default)
        self.apply_size_variant()

        # Width behavior
        if self.width:
            self.input.setFixedWidth(self.width)
        else:
            self.input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.input.setStyleSheet(self.input_style_normal())
        self.input.textChanged.connect(self.on_text_change)

        if self.password:
            self.input.setEchoMode(QLineEdit.Password)

        if self.disabled:
            self.input.setDisabled(True)

        wrap.addWidget(self.input)

        # Suffix icon
        if self.suffix_icon:
            suffix_btn = QPushButton()
            suffix_btn.setIcon(QIcon(self.suffix_icon))
            suffix_btn.setStyleSheet("border: none; padding: 2px;")
            wrap.addWidget(suffix_btn)

        # Clear button
        if self.clearable:
            self.clear_btn = QPushButton("✕")
            self.clear_btn.setFixedWidth(22)
            self.clear_btn.setStyleSheet(
                "border:none; color:#666; font-size:12px; padding:0;"
            )
            self.clear_btn.clicked.connect(lambda: self.input.clear())
            wrap.addWidget(self.clear_btn)

        root.addLayout(wrap)

        # Error label
        self.error_label = QLabel("")
        self.error_label.setStyleSheet(
            f"color: {colors.DANGER_COLOR}; font-size: 12px;"
        )
        self.error_label.setVisible(False)
        root.addWidget(self.error_label)

        self.setLayout(root)

    # -------------------------------------------------------
    # Styling
    # -------------------------------------------------------

    def input_style_normal(self):
        return f"""
            QLineEdit {{
                padding: 8px 10px;
                border-radius: 6px;
                border: 1px solid {colors.BORDER_COLOR};
                background-color: {colors.INPUT_FORM_BG};
                color: {colors.TEXT_PRIMARY};
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border: 1.4px solid {colors.PRIMARY_COLOR};
                background-color: {colors.WHITE};
            }}
        """

    def input_style_error(self):
        return f"""
            QLineEdit {{
                padding: 8px 10px;
                border-radius: 6px;
                border: 1px solid {colors.DANGER_COLOR};
                background-color: {colors.INPUT_FORM_BG};
                color: {colors.TEXT_PRIMARY};
                font-size: 14px;
            }}
        """

    # Size variants
    def apply_size_variant(self):
        size_map = {
            "sm": 28,
            "md": 34,
            "lg": 40,
        }
        self.input.setFixedHeight(size_map.get(self.size_variant, 34))

    # -------------------------------------------------------
    # Logic
    # -------------------------------------------------------

    def on_text_change(self, text: str):
        self.text_changed_raw.emit(text)
        self.debounce_timer.start(self.debounce)

    def emit_debounced(self):
        self.text_changed.emit(self.input.text())

    def set_error(self, message: str):
        self.error_label.setText(message)
        self.error_label.setVisible(True)
        self.input.setStyleSheet(self.input_style_error())

    def clear_error(self):
        self.error_label.setVisible(False)
        self.input.setStyleSheet(self.input_style_normal())

    # API
    def get_value(self):
        return self.input.text()

    def set_value(self, value: str):
        self.input.setText(value)
