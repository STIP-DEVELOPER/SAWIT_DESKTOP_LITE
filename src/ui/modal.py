from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QHBoxLayout,
    QPushButton,
    QWidget,
)
from PyQt5.QtCore import Qt


class Modal(QDialog):
    def __init__(
        self,
        title="Modal",
        message=None,
        content_widget: QWidget = None,
        ok_text="OK",
        cancel_text="Cancel",
        on_ok=None,
        on_cancel=None,
        parent=None,
    ):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.on_ok = on_ok
        self.on_cancel = on_cancel

        self.setMinimumWidth(350)
        self.setStyleSheet(
            """
            QDialog {
                background: #ffffff;
                border-radius: 10px;
            }
            QLabel {
                font-size: 14px;
            }
            QPushButton {
                padding: 8px 16px;
                border-radius: 6px;
            }
            QPushButton#okBtn {
                background: #0078ff;
                color: white;
            }
            QPushButton#cancelBtn {
                background: #d0d0d0;
            }
        """
        )

        layout = QVBoxLayout()

        # ===== CONTENT SECTION =====
        if message:
            layout.addWidget(QLabel(message))

        if content_widget:
            layout.addWidget(content_widget)

        # ===== BUTTON SECTION =====
        btn_layout = QHBoxLayout()

        cancel_btn = QPushButton(cancel_text)
        cancel_btn.setObjectName("cancelBtn")
        cancel_btn.clicked.connect(self._cancel)
        btn_layout.addWidget(cancel_btn)

        ok_btn = QPushButton(ok_text)
        ok_btn.setObjectName("okBtn")
        ok_btn.clicked.connect(self._ok)
        btn_layout.addWidget(ok_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def _ok(self):
        if self.on_ok:
            self.on_ok()
        self.accept()

    def _cancel(self):
        if self.on_cancel:
            self.on_cancel()
        self.reject()
