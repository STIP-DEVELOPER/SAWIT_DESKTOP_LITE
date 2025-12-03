from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt
from utils.icon import get_icon
from ui.chat_bubble import ChatBubble
from ui.feature_button import FeatureButton
from services.ollama_service import OllamaMCPThread


class DashboardPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.messages = [
            {
                "role": "system",
                "content": "Kamu adalah Aitri Agent robot pemupukan sawit. Jawab singkat, akurat, ramah, dalam bahasa Indonesia.",
            }
        ]
        self.is_thinking = False
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(100, 100, 100, 100)
        layout.setSpacing(0)

        header = QLabel("Tanya Aitri")
        header.setAlignment(Qt.AlignCenter)
        header.setFont(QFont("SF Pro Display", 32, QFont.Bold))
        header.setStyleSheet("color: white; padding: 40px 20px 20px 20px;")
        layout.addWidget(header)

        # Input + Send
        top_bar = QWidget()
        top_bar.setFixedHeight(130)
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(60, 30, 60, 30)

        input_box = QWidget()
        input_box.setStyleSheet(
            "background: #1e1b4b; border: 2px solid #6b21d6; border-radius: 10px;"
        )
        input_layout = QHBoxLayout(input_box)
        input_layout.setContentsMargins(20, 20, 20, 20)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Ketik perintah ke AITRI...")
        self.input.setStyleSheet(
            "background: transparent; border: none; color: white; font-size: 17px;"
        )
        self.input.returnPressed.connect(self.send_message)

        self.send_btn = QPushButton()
        self.send_btn.setFixedSize(35, 35)
        self.send_btn.setIcon(QIcon(get_icon("arrow-right.png")))
        self.send_btn.setIconSize(self.send_btn.size() * 0.6)
        self.send_btn.setStyleSheet(
            """
            QPushButton { background: #7c3aed; border-radius: 10px; }
            QPushButton:hover { background: #9d4edd; }
            QPushButton:disabled { background: #4c1d95; opacity: 0.6; }
        """
        )
        self.send_btn.clicked.connect(self.send_message)

        input_layout.addWidget(self.input, 1)
        input_layout.addWidget(self.send_btn)
        top_layout.addWidget(input_box, 1)
        layout.addWidget(top_bar)

        # Feature buttons
        features_bar = QWidget()
        features_bar.setFixedHeight(100)
        fl = QHBoxLayout(features_bar)
        fl.setContentsMargins(60, 20, 60, 20)

        for text, icon, page_idx in [
            ("Inference", "camera.png", 2),
            ("Logs", "logs.png", 3),
            ("Location", "location.png", 6),
            ("Troubleshoot", "tool.png", 7),
            ("Settings", "settings.png", 4),
            ("Upgrade", "upgrade.png", 5),
        ]:
            btn = FeatureButton(text, icon)
            btn.clicked.connect(
                lambda _, i=page_idx: self.parent.stack.setCurrentIndex(i)
            )
            fl.addWidget(btn)
        fl.addStretch()
        layout.addWidget(features_bar)

        # Chat area
        chat_area = QWidget()
        chat_layout = QVBoxLayout(chat_area)
        chat_layout.setContentsMargins(0, 40, 0, 100)
        chat_layout.setSpacing(20)

        self.chat_container = QVBoxLayout()
        self.chat_container.setSpacing(Qt.AlignTop)
        self.chat_container.setSpacing(20)

        chat_layout.addLayout(self.chat_container)
        chat_layout.addStretch()
        layout.addWidget(chat_area, 1)

        self.user_bubble = self.ai_bubble = None

    def send_message(self):
        if self.is_thinking or not (text := self.input.text().strip()):
            return

        self.is_thinking = True
        self.input.setEnabled(False)
        self.send_btn.setEnabled(False)
        self.input.setPlaceholderText("AITRI sedang berfikir...")

        # Hapus bubble lama
        for b in (self.user_bubble, self.ai_bubble):
            if b:
                b.deleteLater()

        # User bubble
        self.user_bubble = ChatBubble(text, is_user=True)
        self.chat_container.addWidget(self.user_bubble)

        # AI bubble sementara
        self.ai_bubble = ChatBubble("Thinking...", is_user=False)
        self.chat_container.addWidget(self.ai_bubble)

        self.input.clear()
        self.messages.append({"role": "user", "content": text})

        # Kirim ke Ollama
        self.thread = OllamaMCPThread(self.messages)
        self.thread.token.connect(self._append_token)
        self.thread.done.connect(self._finish_reply)
        self.thread.start()

    def _append_token(self, token):
        label = self.ai_bubble.findChild(QLabel)
        current = label.text().replace("Thinking...", "", 1)
        label.setText(current + token)

    def _finish_reply(self, reply):
        self.ai_bubble.findChild(QLabel).setText(reply)
        self.messages.append({"role": "assistant", "content": reply})

        self.is_thinking = False
        self.input.setEnabled(True)
        self.send_btn.setEnabled(True)
        self.input.setPlaceholderText("Ketik perintah ke AITRI...")
        self.input.setFocus()
