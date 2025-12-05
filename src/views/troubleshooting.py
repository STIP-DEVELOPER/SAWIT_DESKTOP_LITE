import json
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QTextOption, QTextCursor

from ui.button import Button
from services.ollama_service import OllamaMCPThread
from utils.icon import get_icon


class TroubleshootingPage(QWidget):
    analysis_finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.thread = None
        self.is_running = False
        self.ai_response_buffer = ""  # Kumpulkan semua token di sini
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(25)
        self.setLayout(layout)
        layout.addSpacing(35)

        # Terminal
        self.terminal = QTextEdit()
        self.terminal.setReadOnly(True)
        self.terminal.setMinimumHeight(420)
        self.terminal.setFont(QFont("JetBrains Mono", 12))
        self.terminal.setWordWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)

        # CSS untuk tampilan super clean & modern
        self.terminal.document().setDefaultStyleSheet(
            """
            body { margin: 0; padding: 0; font-family: 'JetBrains Mono'; }
            .status { color: #8b949e; font-weight: bold; margin: 8px 0; }
            .ok { color: #86efac; font-weight: bold; }
            .aitri { color: #93c5fd; font-weight: bold; }
            .response { 
                color: #c8d3f5; 
                font-size: 14px; 
                line-height: 1.8; 
                margin: 16px 0; 
                padding: 16px 20px; 
                background: rgba(59, 130, 246, 0.1); 
                border-left: 4px solid #3b82f6; 
                border-radius: 8px;
            }
            .done { color: #86efac; font-weight: bold; font-size: 15px; margin-top: 20px; }
        """
        )

        self.terminal.setStyleSheet(
            """
            QTextEdit {
                background-color: #0d1117;
                color: #c9d1d9;
                border: 1.5px solid #30363d;
                border-radius: 16px;
                padding: 20px;
            }
        """
        )
        layout.addWidget(self.terminal)

        # Status
        status_layout = QHBoxLayout()
        status_layout.setSpacing(14)
        self.status_icon = QLabel()
        self.status_icon.setFixedSize(30, 30)
        self.status_icon.setScaledContents(True)
        self.status_text = QLabel("Siap melakukan diagnosis")
        self.status_text.setFont(QFont("Segoe UI", 11))
        self.status_text.setStyleSheet("color: #8b949e;")
        status_layout.addWidget(self.status_icon)
        status_layout.addWidget(self.status_text)
        status_layout.addStretch()
        layout.addLayout(status_layout)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.start_button = Button(text="Mulai")
        self.start_button.clicked.connect(self._start_analysis)
        btn_layout.addWidget(self.start_button)

        layout.addLayout(btn_layout)
        self._update_status("idle", "Siap melakukan diagnosis")

    def _update_status(self, state: str, text: str):
        icons = {
            "idle": "circle-off.png",
            "thinking": "brain.png",
            "loading": "loading.png",
            "success": "check-circle.png",
            "error": "alert-circle.png",
        }
        icon = get_icon(icons.get(state, "circle-off.png"))
        if not icon.isNull():
            self.status_icon.setPixmap(icon.pixmap(26, 26))
        self.status_text.setText(text)

    def _start_analysis(self):
        if self.is_running:
            return
        self.is_running = True
        self.ai_response_buffer = ""  # Reset buffer
        self.start_button.setEnabled(False)
        self.start_button.setText("AI sedang bekerja...")
        self._update_status("thinking", "Mengakses memori sistem...")

        self.terminal.clear()
        self.terminal.append(
            '<div class="status">[NEURAL]</div>Memindai kondisi terbaru'
        )

        try:
            with open("logs/data.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            recent_data = data[-10:]
            data_str = json.dumps(recent_data, indent=2, ensure_ascii=False)
        except Exception as e:
            self.terminal.append(
                f'<div class="status" style="color:#f87171">[ERROR]</div>Gagal mengakses data sistem'
            )
            self._update_status("error", "Sistem tidak responsif")
            self._reset_buttons()
            return

        self.terminal.append(
            '<div class="ok">[OK]</div>Data real-time berhasil diakses'
        )
        self.terminal.append('<div class="aitri">[AITRI]</div>Sedang menganalisis...\n')
        self._update_status("loading", "sedang berpikir...")

        messages = [
            {
                "role": "system",
                "content": "Kamu adalah AITRI — AI canggih untuk robot sawit. "
                "Analisis 10 data terbaru. Berikan diagnosis tajam + solusi praktis dalam bahasa Indonesia sederhana, maksimal 3 kalimat.",
            },
            {
                "role": "user",
                "content": f"Analisis kondisi robot dari data ini:\n\n```json\n{data_str}\n```\n\n"
                "Apa masalahnya? Bagaimana cara memperbaikinya?",
            },
        ]

        self.thread = OllamaMCPThread(messages)
        self.thread.token.connect(self._on_token_received)
        self.thread.done.connect(self._on_analysis_done)
        self.thread.start()

    def _on_token_received(self, text: str):
        if not text.strip():
            return

        # KUMPULKAN SEMUA TOKEN DI BUFFER
        self.ai_response_buffer += text

        # Update tampilan langsung (tapi tetap satu blok)
        cursor = self.terminal.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.select(QTextCursor.BlockUnderCursor)

        # Hapus blok respons lama jika ada
        if cursor.selectedText().startswith("AITRI sedang mengetik"):
            cursor.removeSelectedText()
            cursor.deletePreviousChar()  # hapus newline

        # Tampilkan buffer sementara dengan efek "typing"
        cursor.insertHtml(
            f'<div class="response"><strong>AITRI:</strong> {self.ai_response_buffer}_</div>'
        )
        self.terminal.setTextCursor(cursor)
        self.terminal.ensureCursorVisible()

    def _on_analysis_done(self, final_text: str):
        clean_response = self.ai_response_buffer.strip()
        if not clean_response:
            clean_response = "Tidak ada masalah terdeteksi pada sistem."

        self._update_status("success", "Diagnosis selesai")
        self.start_button.setText("Diagnosis Ulang")
        self.start_button.setEnabled(True)
        self.is_running = False

    def _reset_buttons(self):
        self.start_button.setText("Mulai Diagnosis...")
        self.start_button.setEnabled(True)
        self.is_running = False

    def _on_next_clicked(self):
        self.analysis_finished.emit()
