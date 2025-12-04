import json
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon

from ui.button import Button
from services.ollama_service import OllamaMCPThread
from utils.icon import get_icon


class TroubleshootingPage(QWidget):
    analysis_finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.thread = None
        self.is_running = False
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(25)
        self.setLayout(layout)

        # Header — Super Premium
        title = QLabel("AITRI Diagnostics Sistem")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title.setStyleSheet("color: #ffffff; letter-spacing: 0.5px;")
        layout.addWidget(title)

        layout.addSpacing(35)

        # Terminal — Futuristik
        self.terminal = QTextEdit()
        self.terminal.setReadOnly(True)
        self.terminal.setMinimumHeight(420)
        self.terminal.setFont(QFont("JetBrains Mono", 11, QFont.Medium))
        self.terminal.setStyleSheet(
            """
            QTextEdit {
                background-color: #0d1117;
                color: #c9d1d9;
                border: 1.5px solid #30363d;
                border-radius: 16px;
                padding: 20px;
                line-height: 1.6;
                selection-background-color: #1f6feb;
            }
        """
        )
        layout.addWidget(self.terminal)

        # Status Indicator
        status_layout = QHBoxLayout()
        status_layout.setSpacing(14)

        self.status_icon = QLabel()
        self.status_icon.setFixedSize(30, 30)
        self.status_icon.setScaledContents(True)

        self.status_text = QLabel("Siap melakukan diagnosis")
        self.status_text.setFont(QFont("Segoe UI", 11, QFont.Medium))
        self.status_text.setStyleSheet("color: #8b949e;")

        status_layout.addWidget(self.status_icon)
        status_layout.addWidget(self.status_text)
        status_layout.addStretch()
        layout.addLayout(status_layout)

        # Buttons — High-End
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.start_button = Button(
            text="Mulai Diagnosis AI", icon_path=get_icon("brain.png")
        )
        self.start_button.setFixedHeight(56)
        self.start_button.setStyleSheet(
            """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #6366f1, stop:1 #8b5cf6);
                color: white;
                border-radius: 14px;
                padding: 14px 36px;
                font-size: 16px;
                font-weight: bold;
                border: 1px solid rgba(255,255,255,0.1);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #7c3aed, stop:1 #a78bfa);
                transform: translateY(-1px);
            }
            QPushButton:pressed { background: #5b21b6; }
            QPushButton:disabled { background: #1e1b4b; color: #6b7280; }
        """
        )
        self.start_button.clicked.connect(self._start_analysis)
        btn_layout.addWidget(self.start_button)

        self.next_button = Button(
            text="Lanjut ke Dashboard", icon_path=get_icon("arrow-right.png")
        )
        self.next_button.setFixedHeight(56)
        self.next_button.setEnabled(False)
        self.next_button.setStyleSheet(
            """
            QPushButton:disabled { background: #1e293b; color: #64748b; border: 1px solid #334155; }
            QPushButton:enabled {
                background-color: #16a34a;
                color: white;
                border-radius: 14px;
                padding: 14px 36px;
                font-size: 16px;
                font-weight: bold;
                border: 1px solid rgba(255,255,255,0.15);
            }
        """
        )
        self.next_button.clicked.connect(self._on_next_clicked)
        btn_layout.addWidget(self.next_button)

        layout.addLayout(btn_layout)

        self._update_status("idle", "Siap melakukan diagnosis")

    def _update_status(self, state: str, text: str):
        icon_map = {
            "idle": "circle-off.png",
            "thinking": "brain.png",
            "loading": "loading.png",
            "success": "check-circle.png",
            "error": "alert-circle.png",
        }
        icon_name = icon_map.get(state, "circle-off.png")
        icon = get_icon(icon_name)

        if not icon.isNull():
            self.status_icon.setPixmap(icon.pixmap(26, 26))
        else:
            from PyQt5.QtGui import QPixmap, QPainter, QBrush, QColor

            pix = QPixmap(26, 26)
            pix.fill(Qt.transparent)
            p = QPainter(pix)
            p.setRenderHint(QPainter.Antialiasing)
            p.setBrush(QBrush(QColor("#666666")))
            p.setPen(Qt.NoPen)
            p.drawEllipse(3, 3, 20, 20)
            p.end()
            self.status_icon.setPixmap(pix)

        self.status_text.setText(text)

    def _start_analysis(self):
        if self.is_running:
            return
        self.is_running = True

        self.start_button.setEnabled(False)
        self.start_button.setText("AI sedang bekerja...")
        self.next_button.setEnabled(False)
        self._update_status("thinking", "Mengakses memori sistem...")

        self.terminal.clear()
        self.terminal.append(
            "<span style='color:#8b949e'>[NEURAL]</span> Memindai kondisi robot terbaru"
        )

        try:
            with open("logs/data.json", "r", encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, list):
                raise ValueError("Data tidak valid")

            recent_data = data[-10:]  # HANYA 10 TERAKHIR
            data_str = json.dumps(recent_data, indent=2, ensure_ascii=False)

        except Exception as e:
            self.terminal.append(
                f"<span style='color:#f87171'>[ERROR]</span> Gagal mengakses memori sistem"
            )
            self._update_status("error", "Sistem tidak responsif")
            self._reset_buttons()
            return

        self.terminal.append(
            "<span style='color:#86efac'>[OK]</span> Data real-time berhasil diakses"
        )
        self.terminal.append(
            "<span style='color:#93c5fd'>[AITRI]</span> Sedang menganalisis pola perilaku robot...\n"
        )
        self._update_status("loading", "AITRI sedang berpikir mendalam...")

        messages = [
            {
                "role": "system",
                "content": "Kamu adalah AITRI — kecerdasan buatan tingkat tinggi untuk robot sawit. "
                "Analisis 10 data sistem terbaru. Deteksi anomali, error, atau masalah performa. "
                "Berikan diagnosis tajam dan solusi praktis dalam bahasa Indonesia yang sangat mudah dipahami petani. "
                "Maksimal 3 kalimat. Jawab langsung, tanpa format teknis.",
            },
            {
                "role": "user",
                "content": f"Analisis kondisi robot dari 10 data terbaru ini:\n\n```json\n{data_str}\n```\n\n"
                "Apa yang salah? Bagaimana cara memperbaikinya?",
            },
        ]

        self.thread = OllamaMCPThread(messages)
        self.thread.token.connect(self._on_token_received)
        self.thread.done.connect(self._on_analysis_done)
        self.thread.start()

    def _on_token_received(self, text: str):
        if text.strip():
            escaped = text.replace("\n", "<br>").replace(" ", "&nbsp;")
            self.terminal.append(f"<span style='color:#a5b4fc'>{escaped}</span>")
            self.terminal.verticalScrollBar().setValue(
                self.terminal.verticalScrollBar().maximum()
            )

    def _on_analysis_done(self, final_text: str):
        self.terminal.append(
            "\n<span style='color:#86efac; font-weight: bold;'>[DIAGNOSIS SELESAI]</span>"
        )
        self._update_status("success", "Diagnosis selesai")
        self.next_button.setEnabled(True)
        self.start_button.setText("Diagnosis Ulang")
        self.start_button.setEnabled(True)
        self.is_running = False

    def _reset_buttons(self):
        self.start_button.setText("Mulai Diagnosis AI")
        self.start_button.setEnabled(True)
        self.is_running = False

    def _on_next_clicked(self):
        self.analysis_finished.emit()
