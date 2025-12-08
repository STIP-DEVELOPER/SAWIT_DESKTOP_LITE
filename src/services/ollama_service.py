import json
from PyQt5.QtCore import QThread, pyqtSignal
import ollama


def nyalakan_led():
    """Tool: Hitung a + b + 1"""
    print("hotungsd")
    return "LED dinyalakan!"


TOOLS = {
    "nyalakan_led": nyalakan_led,
}


class OllamaMCPThread(QThread):
    token = pyqtSignal(str)
    done = pyqtSignal(str)

    def __init__(self, messages: list):
        super().__init__()
        self.system_prompt = {
            "role": "system",
            "content": (
                "Kamu adalah AITRI, AI assistant traktor pemupuk sawit otomatis yang dibuat oleh Mr. Misdar. "
                "AITRI harus menjawab dengan singkat, jelas, dan bahasa Indonesia lapangan. "
                "AITRI mengerti sistem YOLO, jarak 10–200 cm, kiri/kanan, GPS, log, dan kontrol alat."
            ),
        }

        self.messages = [self.system_prompt] + messages[:]

    def run(self):
        full_response = ""

        while True:
            try:
                stream = ollama.chat(model="aitri", messages=self.messages, stream=True)

                print(f"steam={stream}")

                response_text = ""
                for chunk in stream:
                    if content := chunk["message"].get("content"):
                        response_text += content
                        full_response += content
                        self.token.emit(content)

                print(f"response text = {response_text}")

                if "{" in response_text and "}" in response_text:
                    try:
                        start = response_text.index("{")
                        end = response_text.rindex("}") + 1
                        json_str = response_text[start:end]
                        tool_call = json.loads(json_str)

                        tool_name = tool_call.get("tool")

                        print(f"tool name = {tool_name}")
                        if tool_name in TOOLS:
                            func = TOOLS[tool_name]
                            args = tool_call.get("arguments", {})
                            result = func(**args)

                            self.token.emit(
                                f"\nMenghitung {tool_name.replace('_', ' ')}... {result}\n"
                            )

                            self.messages.append(
                                {"role": "assistant", "content": response_text}
                            )
                            self.messages.append(
                                {"role": "tool", "content": str(result)}
                            )

                            full_response = ""
                            continue
                    except Exception:
                        pass
                break

            except Exception as e:
                self.done.emit(f"[ERROR] {e}")
                return

        self.done.emit(full_response.strip())
