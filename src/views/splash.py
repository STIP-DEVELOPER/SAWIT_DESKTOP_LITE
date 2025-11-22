from PyQt5.QtWidgets import QSplashScreen, QApplication
from PyQt5.QtGui import QPixmap, QFont, QColor, QPainter
from PyQt5.QtCore import Qt


class SplashScreen(QSplashScreen):
    def __init__(self):
        # --- FULLSCREEN FIX ---
        # Buat pixmap sesuai resolusi layar penuh
        screen = QApplication.primaryScreen()
        size = screen.size()
        pixmap = QPixmap(size)
        pixmap.fill(QColor("#111111"))  # dark background

        # Optional: jika mau gambar/logo di tengah
        # painter = QPainter(pixmap)
        # logo = QPixmap("assets/logo.png")
        # x = (size.width() - logo.width()) // 2
        # y = (size.height() - logo.height()) // 2 - 80
        # painter.drawPixmap(x, y, logo)
        # painter.end()

        super().__init__(pixmap)

        # --- TEXT STYLE ---
        font = QFont("Arial", 20)
        font.setBold(True)
        self.setFont(font)

        self.showMessage(
            "Initializing...",
            Qt.AlignHCenter | Qt.AlignBottom,
            QColor("#DDDDDD"),  # light gray text
        )

        # Remove window frame (lebih clean)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setStyleSheet("background-color: #111111;")  # just in case

        # Fullscreen mode
        self.showFullScreen()

    # Optional: method update progress text
    def update_message(self, text: str):
        self.showMessage(
            text,
            Qt.AlignHCenter | Qt.AlignBottom,
            QColor("#DDDDDD"),
        )
