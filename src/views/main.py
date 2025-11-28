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
from views.home import HomePage
from views.logger import LoggerPage
from views.setting import SettingsPage
from views.upgrade import UpgradePage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Sawit Desktop")
        self._set_responsive_geometry()

        self.stack = QStackedWidget()
        self.header_widget = QWidget()
        self.header_layout = QHBoxLayout()
        self.header_layout.setContentsMargins(20, 20, 20, 0)
        self.header_layout.setSpacing(30)

        # Back button
        self.back_btn = Button(text="Back", icon_path=get_icon("arrow-left-1.png"))
        self.back_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.back_btn.setVisible(False)

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

        self.exit_btn = Button(text="Exit", icon_path=get_icon("exit.png"))
        self.exit_btn.clicked.connect(self._confirm_exit)

        left_box = QHBoxLayout()
        left_box.addWidget(self.back_btn)
        left_box.addWidget(self.title_label)
        left_box.addStretch(1)

        self.header_layout.addLayout(left_box)
        self.header_layout.addWidget(self.exit_btn, alignment=Qt.AlignRight)

        self.header_widget.setLayout(self.header_layout)

        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(5)

        main_layout.addWidget(self.header_widget)
        main_layout.addWidget(self.stack)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        self.dashboard_page = DashboardPage(parent=self)
        self.page_inference = HomePage(parent=self)
        self.page_logs = LoggerPage(parent=self)
        self.page_settings = SettingsPage(parent=self)
        self.page_upgrade = UpgradePage(parent=self)

        self.stack.addWidget(self.wrap_with_scroll(self.dashboard_page))  # index 0
        self.stack.addWidget(self.wrap_with_scroll(self.page_inference))  # index 1
        self.stack.addWidget(self.wrap_with_scroll(self.page_logs))  # index 2
        self.stack.addWidget(self.wrap_with_scroll(self.page_settings))  # index 3
        self.stack.addWidget(self.wrap_with_scroll(self.page_upgrade))  # index 4

        self.stack.setCurrentIndex(0)

        self._update_header_visibility()
        self.stack.currentChanged.connect(self._update_header_visibility)

    def wrap_with_scroll(self, widget):
        scroll = QScrollArea()
        scroll.setWidget(widget)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # hanya vertical
        return scroll

    def _update_header_visibility(self):
        current = self.stack.currentIndex()
        self.back_btn.setVisible(current != 0)

        titles = ["Dashboard", "Inference", "Logs", "Settings", "Upgrade"]
        self.title_label.setText(titles[current])

    def _set_responsive_geometry(self):

        self.showFullScreen()

    def _confirm_exit(self):
        modal = Modal(title="Apakah yakin anda mau keluar?", on_ok=self.close)
        modal.exec_()
