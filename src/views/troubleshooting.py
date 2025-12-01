from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTextEdit,
    QSizePolicy,
)
from PyQt5.QtCore import Qt, QTimer

from ui.button import Button


class TroubleshootingPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self._build_ui()
        self._start_terminal_animation()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Terminal-like display
        self.terminal = QTextEdit()
        self.terminal.setReadOnly(True)
        self.terminal.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.terminal.setStyleSheet(
            """
            QTextEdit {
                background-color: #0d0d0d;
                color: #00ff00;
                font-family: 'Courier New', Consolas, monospace;
                font-size: 14px;
                border: 1px solid #333;
                border-radius: 8px;
                padding: 15px;
            }
        """
        )
        layout.addWidget(self.terminal)

        # Tombol Lanjutkan (akan otomatis hilang setelah pindah)
        self.next_button = Button(text="Lanjutkan →", icon_path=None)
        self.next_button.setEnabled(False)
        self.next_button.setStyleSheet(
            """
            QPushButton {
                background-color: #0066cc;
                color: white;
                padding: 12px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 15px;
            }
            QPushButton:disabled {
                background-color: #333;
                color: #666;
            }
        """
        )
        self.next_button.clicked.connect(self._on_next_clicked)
        layout.addWidget(self.next_button, alignment=Qt.AlignRight)

        self.setLayout(layout)

    def _start_terminal_animation(self):
        self.logs = [
            "[INFO] Memulai inisialisasi sistem...",
            "[INFO] Memuat konfigurasi aplikasi",
            "[OK]   Konfigurasi berhasil dimuat",
            "[INFO] Memeriksa dependensi PyQt5",
            "[OK]   PyQt5 & WebEngine terdeteksi",
            "[INFO] Menghubungkan ke GPS module",
            "[OK]   GPS module siap",
            "[INFO] Memuat model AI inference",
            "[OK]   Model YOLO berhasil dimuat",
            "[INFO] Menyiapkan antarmuka kamera",
            "[OK]   Kamera terdeteksi dan aktif",
            "[SUCCESS] Semua sistem siap!",
            "",
            "→ Mengarahkan ke Dashboard...",
        ]

        self.current_line = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self._print_next_line)
        self.timer.start(400)  # Sedikit lebih lambat agar terbaca

    def _print_next_line(self):
        if self.current_line < len(self.logs):
            line = self.logs[self.current_line]
            self.terminal.append(line)
            self.current_line += 1
        else:
            self.timer.stop()
            self.next_button.setEnabled(True)
            self.next_button.setStyleSheet(
                """
                QPushButton {
                    background-color: #00aa00;
                    color: white;
                    padding: 12px;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 15px;
                }
            """
            )

    def _on_next_clicked(self):
        self._auto_proceed_to_dashboard()
