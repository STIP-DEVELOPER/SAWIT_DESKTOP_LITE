from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QStackedWidget,
)

from ui.styles import GlobalStyle
from ui.navigation import TopNavigation

from views.home import HomePage
from views.logger import LoggerPage
from views.setting import SettingsPage
from views.upgrade import UpgradePage


class MainWindow(QMainWindow):
    globalStyle = GlobalStyle()

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Sawit APP")
        self._set_responsive_geometry()

        self.setStyleSheet(self.globalStyle.theme())

        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self.navigation = TopNavigation()
        self.navigation.navigate.connect(self.on_navigate)
        self.navigation.exit_clicked.connect(self.close)

        self.pages = QStackedWidget()

        self.page_home = HomePage()
        self.page_logger = LoggerPage()
        self.page_settings = SettingsPage()
        self.page_upgrade = UpgradePage()

        self.pages.addWidget(self.page_home)  # index 0
        self.pages.addWidget(self.page_logger)  # index 1
        self.pages.addWidget(self.page_settings)  # index 2
        self.pages.addWidget(self.page_upgrade)  # index 3  ← TAMBAHKAN

        root_layout.addWidget(self.navigation)
        root_layout.addWidget(self.pages)
        self.setCentralWidget(root)

    def _set_responsive_geometry(self):
        self.showFullScreen()

    def on_navigate(self, index):
        self.pages.setCurrentIndex(index)

    def resizeEvent(self, event):
        super().resizeEvent(event)
