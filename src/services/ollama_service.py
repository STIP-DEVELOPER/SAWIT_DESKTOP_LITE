import subprocess
import threading
from PyQt5.QtCore import QThread, pyqtSignal
import ollama


def start_ollama_server():
    """Jalankan ollama serve di background (sekali saja)"""
    subprocess.Popen(
        ["ollama", "serve"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


threading.Thread(target=start_ollama_server, daemon=True).start()


class OllamaStreamThread(QThread):
    token = pyqtSignal(str)
    done = pyqtSignal(str)

    def __init__(self, messages, model="aitri-sawit"):
        super().__init__()
        self.messages = messages[:]
        self.model = model

    def run(self):
        full_response = ""
        try:
            stream = ollama.chat(model=self.model, messages=self.messages, stream=True)
            for chunk in stream:
                if content := chunk["message"].get("content"):
                    full_response += content
                    self.token.emit(content)
            self.done.emit(full_response)
        except Exception as e:
            self.done.emit(f"[ERROR] {e}")
