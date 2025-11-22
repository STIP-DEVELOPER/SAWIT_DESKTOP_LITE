from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal, QSize

from configs import colors
from ui.modal import Modal
from utils.icon import get_icon


class NavItem(QPushButton):
    def __init__(self, text, icon_name=None):
        super().__init__(text)

        self.active = False  # ← indikator active

        self.setFixedHeight(30)
        self.setCursor(Qt.PointingHandCursor)

        if icon_name:
            icon = get_icon(icon_name)
            self.setIcon(icon)
            self.setIconSize(QSize(22, 22))

        self.update_style()

    def set_active(self, active: bool):
        self.active = active
        self.update_style()

    def update_style(self):
        if self.active:
            # STYLE SAAT ACTIVE
            self.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: {colors.PRIMARY_COLOR};
                    color: {colors.TEXT_ON_PRIMARY};
                    border-radius: 12px;
                    padding-left: 16px;
                    padding-right: 16px;
                    font-size: 16px;
                    font-weight: 600;
                }}
                QPushButton:hover {{
                    background-color: {colors.PRIMARY_HOVER};
                }}
            """
            )
        else:
            # STYLE NORMAL
            self.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: {colors.SURFACE_COLOR};
                    color: {colors.TEXT_PRIMARY};
                    border: none;
                    border-radius: 12px;
                    padding-left: 16px;
                    padding-right: 16px;
                    font-size: 16px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background-color: {colors.PRIMARY_HOVER};
                    color: {colors.TEXT_ON_PRIMARY};
                }}
            """
            )


class TopNavigation(QWidget):
    navigate = pyqtSignal(int)
    exit_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.setFixedHeight(70)
        self.setStyleSheet(
            f"""
            background: {colors.SURFACE_COLOR};
            border-bottom: 1px solid {colors.BORDER_COLOR};
            """
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)

        self.btn_home = NavItem("Home", "home.png")
        self.btn_logs = NavItem("Logs", "logs.png")
        self.btn_settings = NavItem("Settings", "settings.png")
        self.btn_exit = NavItem("Exit", "exit.png")

        self.buttons = [self.btn_home, self.btn_logs, self.btn_settings]

        layout.addWidget(self.btn_home)
        layout.addWidget(self.btn_logs)
        layout.addWidget(self.btn_settings)
        layout.addStretch()
        layout.addWidget(self.btn_exit)

        self.btn_home.clicked.connect(lambda: self.on_nav_clicked(0))
        self.btn_logs.clicked.connect(lambda: self.on_nav_clicked(1))
        self.btn_settings.clicked.connect(lambda: self.on_nav_clicked(2))
        self.btn_exit.clicked.connect(self.on_exit)

        self.set_active(0)  # Default: Home active

    def on_nav_clicked(self, index):
        self.set_active(index)
        self.navigate.emit(index)

    def set_active(self, index):
        for i, btn in enumerate(self.buttons):
            btn.set_active(i == index)

    def on_exit(self):
        modal = Modal(
            title="Apakah yakin anda mau keluar?", on_ok=self.exit_clicked.emit
        )
        modal.exec_()
