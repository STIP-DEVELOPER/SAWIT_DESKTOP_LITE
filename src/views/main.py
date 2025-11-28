from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QStackedWidget,
    QScrollArea,
)
from PyQt5.QtCore import Qt

from ui.button import Button
from ui.modal import Modal
from utils.icon import get_icon

from views.dashboard import DashboardPage
from views.inference import InferencePage
from views.logger import LoggerPage
from views.setting import SettingsPage
from views.upgrade import UpgradePage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.showFullScreen()
        self.setWindowTitle("Sawit Desktop")
        self._set_responsive_geometry()

        # STACK (halaman utama)
        self.stack = QStackedWidget()

        # HEADER ---------------------------------------------------------
        self.header_widget = QWidget()

        self.header_layout = QHBoxLayout()

        self.header_layout.setContentsMargins(10, 20, 20, 10)
        self.header_layout.setSpacing(30)

        self.header_widget.setStyleSheet(
            """
            QWidget {
                padding-top: 5px;
                padding-bottom: 5px;
            }
        """
        )

        # Back
        self.back_btn = Button(text="Back", icon_path=get_icon("arrow-left.png"))
        self.back_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.back_btn.setVisible(False)

        # Title
        self.title_label = QLabel("Dashboard")
        self.title_label.setStyleSheet(
            """
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: bold;
            }
        """
        )

        # Exit
        self.exit_btn = Button(text="Exit", icon_path=get_icon("exit.png"))
        self.exit_btn.clicked.connect(self._confirm_exit)

        left_box = QHBoxLayout()
        left_box.addWidget(self.back_btn)
        left_box.addWidget(self.title_label)
        left_box.addStretch(1)

        self.header_layout.addLayout(left_box)
        self.header_layout.addWidget(self.exit_btn, alignment=Qt.AlignRight)
        self.header_widget.setLayout(self.header_layout)

        # MAIN LAYOUT ----------------------------------------------------
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        main_layout.addWidget(self.header_widget)
        main_layout.addWidget(self.stack)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # CREATE PAGES ---------------------------------------------------
        self._load_pages()

        self._update_header()
        self.stack.currentChanged.connect(self._update_header)

    def _set_responsive_geometry(self):
        self.showFullScreen()

    # ------------------------------------------------------------------
    # WRAP PAGE WITH SCROLL AREA
    # ------------------------------------------------------------------
    def _wrap_scroll(self, widget):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setStyleSheet("background-color: #0D0D0D;")
        scroll.setWidget(widget)
        return scroll

    def _load_pages(self):
        dashboard = self._wrap_scroll(DashboardPage(parent=self))
        inference = self._wrap_scroll(InferencePage(parent=self))
        logs = self._wrap_scroll(LoggerPage(parent=self))
        settings = self._wrap_scroll(SettingsPage(parent=self))
        upgrade = self._wrap_scroll(UpgradePage(parent=self))

        self.stack.addWidget(dashboard)  # 0
        self.stack.addWidget(inference)  # 1
        self.stack.addWidget(logs)  # 2
        self.stack.addWidget(settings)  # 3
        self.stack.addWidget(upgrade)  # 4

    # -----------------------------------------------------------
    def _update_header(self):
        index = self.stack.currentIndex()
        self.back_btn.setVisible(index != 0)

        titles = ["Dashboard", "Inference", "Logs", "Settings", "Upgrade"]
        self.title_label.setText(titles[index])

    # -----------------------------------------------------------
    def _confirm_exit(self):
        modal = Modal(title="Apakah yakin anda mau keluar?", on_ok=self.close)
        modal.exec_()
