# dashboard.py – FINAL: Input & Send Button DISABLED saat Thinking (ANTI-CRASH)
import subprocess
import threading
import ollama
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont, QIcon
from utils.icon import get_icon


# ==================== JALANKAN OLLAMA ====================
def start_ollama():
    subprocess.Popen(
        ["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )


threading.Thread(target=start_ollama, daemon=True).start()


# ==================== THREAD CHAT (aitri-sawit) ====================
class StreamingThread(QThread):
    token = pyqtSignal(str)
    done = pyqtSignal(str)

    def __init__(self, messages):
        super().__init__()
        self.messages = messages[:]

    def run(self):
        full = ""
        try:
            stream = ollama.chat(
                model="aitri-sawit", messages=self.messages, stream=True
            )
            for chunk in stream:
                if content := chunk["message"].get("content"):
                    full += content
                    self.token.emit(content)
            self.done.emit(full)
        except Exception as e:
            self.done.emit(f"[ERROR] {e}")


# ==================== BUBBLE CHAT (User Kiri, AI Kanan) ====================
class ChatBubble(QWidget):
    def __init__(self, text: str, is_user: bool = False):
        super().__init__()
        hbox = QHBoxLayout(self)
        hbox.setContentsMargins(60, 12, 60, 12)

        label = QLabel(text)
        label.setWordWrap(True)
        label.setFont(QFont("SF Pro Display", 16))
        label.setContentsMargins(20, 16, 20, 16)

        if is_user:
            label.setStyleSheet(
                """
                background: #2d1b69; color: #e6d9ff;
                border-radius: 24px;
                border-bottom-left-radius: 8px;
                border: 1px solid #5b21b6;
            """
            )
            hbox.addWidget(label)
            hbox.addStretch()
        else:
            label.setStyleSheet(
                """
                background: #7c3aed; color: white;
                border-radius: 24px;
                border-bottom-right-radius: 8px;
            """
            )
            hbox.addStretch()
            hbox.addWidget(label)


# ==================== TOMBOL FITUR ====================
class FeatureButton(QPushButton):
    def __init__(self, text, icon_path=None):
        super().__init__(text)
        self.setFixedHeight(50)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(
            """
            QPushButton {
                background: #1e1b4b; color: #e0d4ff;
                border: 1px solid #5b21b6; border-radius: 16px;
                padding: 0 26px; font-size: 14px; font-weight: 600;
            }
            QPushButton:hover { background: #3a1b8a; border-color: #9d4edd; }
            QPushButton:pressed { background: #5b21b6; }
        """
        )
        if icon_path:
            self.setIcon(QIcon(get_icon(icon_path)))


# ==================== DASHBOARD UTAMA (AMAN & STABIL) ====================
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

        # ==================== INPUT + SEND BUTTON DI DALAM ====================
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
        self.input.returnPressed.connect(self.send)

        self.send_btn = QPushButton()
        self.send_btn.setFixedSize(35, 35)
        self.send_btn.setIcon(QIcon(get_icon("arrow-right.png")))
        self.send_btn.setIconSize(self.send_btn.size() * 0.6)
        self.send_btn.setStyleSheet(
            """
            QPushButton { background: #7c3aed; border-radius: 10px; }
            QPushButton:hover { background: #9d4edd; }
            QPushButton:pressed { background: #5b21b6; }
            QPushButton:disabled { background: #4c1d95; opacity: 0.6; }
        """
        )
        self.send_btn.clicked.connect(self.send)

        input_layout.addWidget(self.input, 1)
        input_layout.addWidget(self.send_btn)
        top_layout.addWidget(input_box, 1)
        layout.addWidget(top_bar)

        # ==================== TOMBOL FITUR ====================
        features_bar = QWidget()
        features_bar.setFixedHeight(100)
        features_layout = QHBoxLayout(features_bar)
        features_layout.setContentsMargins(60, 20, 60, 20)

        buttons = [
            ("Inference", "camera.png", 2),
            ("Logs", "logs.png", 3),
            ("Location", "location.png", 6),
            ("Troubleshoot", "tool.png", 7),
            ("Settings", "settings.png", 4),
            ("Upgrade", "upgrade.png", 5),
        ]
        for text, icon, idx in buttons:
            btn = FeatureButton(text, icon)
            btn.clicked.connect(lambda _, i=idx: self.parent.stack.setCurrentIndex(i))
            features_layout.addWidget(btn)
        features_layout.addStretch()
        layout.addWidget(features_bar)

        # ==================== AREA CHAT ====================
        chat_area = QWidget()
        chat_layout = QVBoxLayout(chat_area)
        chat_layout.setContentsMargins(0, 40, 0, 100)
        chat_layout.setSpacing(20)

        self.chat_container = QVBoxLayout()
        self.chat_container.setSpacing(20)
        self.chat_container.setAlignment(Qt.AlignTop)

        self.user_bubble = None
        self.ai_bubble = None

        chat_layout.addLayout(self.chat_container)
        chat_layout.addStretch()
        layout.addWidget(chat_area, 1)

    def send(self):
        if self.is_thinking:
            return

        text = self.input.text().strip()
        if not text:
            return

        self.is_thinking = True
        self.input.setEnabled(False)
        self.send_btn.setEnabled(False)
        self.input.setPlaceholderText("AITRI sedang berfikir...")

        if self.user_bubble:
            self.user_bubble.deleteLater()
        if self.ai_bubble:
            self.ai_bubble.deleteLater()

        self.user_bubble = ChatBubble(text, is_user=True)
        self.chat_container.addWidget(self.user_bubble)

        self.ai_bubble = ChatBubble("Thinking...", is_user=False)
        self.chat_container.addWidget(self.ai_bubble)

        self.input.clear()
        self.messages.append({"role": "user", "content": text})

        self.thread = StreamingThread(self.messages)
        self.thread.token.connect(
            lambda t: self.ai_bubble.findChild(QLabel).setText(
                self.ai_bubble.findChild(QLabel).text().replace("Thinking...", "") + t
            )
        )
        self.thread.done.connect(lambda reply: self.finish_reply(reply))
        self.thread.start()

    def finish_reply(self, reply):
        # Update jawaban akhir
        self.ai_bubble.findChild(QLabel).setText(reply)
        self.messages.append({"role": "assistant", "content": reply})

        # Aktifkan kembali input & tombol
        self.is_thinking = False
        self.input.setEnabled(True)
        self.send_btn.setEnabled(True)
        self.input.setPlaceholderText("Ketik perintah ke AITRI...")
        self.input.setFocus()


# ==================== TES LANGSUNG ====================
if __name__ == "__main__":
    app = QApplication([])
    app.setStyle("Fusion")
    win = DashboardPage()
    win.resize(1200, 900)
    win.show()
    app.exec_()
