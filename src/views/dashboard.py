from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QGridLayout,
    QFrame,
)

from utils.icon import get_icon


class DashboardCard(QFrame):
    clicked = pyqtSignal()

    def __init__(self, title, icon_path=None):
        super().__init__()

        self.setObjectName("dashboardCard")
        self.setCursor(Qt.PointingHandCursor)

        self.setStyleSheet(
            """
            QFrame#dashboardCard {
                background-color: #1A1A1A;
                border: 1px solid #242424;
                border-radius: 20px;
                padding: 24px;
            }
            QFrame#dashboardCard:hover {
                background-color: #1F1F1F;
                border-color: #3A3A3A;
            }
            QLabel {
                color: #EDEDED;
                font-size: 14px;
                font-weight: 600;
            }
        """
        )

        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignCenter)

        # Icon
        if icon_path:
            icon_label = QLabel()
            icon_label.setPixmap(get_icon(icon_path).pixmap(48, 48))
            icon_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(icon_label)

        # Title
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        self.setLayout(layout)

    def mousePressEvent(self, event):
        self.clicked.emit()


class DashboardPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(26, 26, 26, 26)
        layout.setSpacing(25)

        # GRID CARDS
        grid = QGridLayout()
        grid.setSpacing(24)

        card_inference = DashboardCard("Inference", "camera.png")
        card_logs = DashboardCard("Logs", "logs.png")
        card_settings = DashboardCard("Settings", "settings.png")
        card_upgrade = DashboardCard("Upgrade", "upgrade.png")

        grid.addWidget(card_inference, 0, 0)
        grid.addWidget(card_logs, 0, 1)
        grid.addWidget(card_settings, 1, 0)
        grid.addWidget(card_upgrade, 1, 1)

        layout.addLayout(grid)
        self.setLayout(layout)

        self.setStyleSheet("background-color: #0D0D0D;")

        card_inference.clicked.connect(lambda: self.parent.stack.setCurrentIndex(1))
        card_logs.clicked.connect(lambda: self.parent.stack.setCurrentIndex(2))
        card_settings.clicked.connect(lambda: self.parent.stack.setCurrentIndex(3))
        card_upgrade.clicked.connect(lambda: self.parent.stack.setCurrentIndex(4))
