# demo_agent.py – AI Agent Gemma 3 + Tool Calling (Modular)
import ollama
import json


import serial
import time

ser = serial.Serial("/dev/cu.usbserial-1410", baudrate=9600, timeout=1)


# ===== TOOLS =====
def calculate(a: float, b: float):
    """Tool: Hitung a + b + 1"""
    return a + b + 2


def control_led(action: str):
    """
    Tool: Kontrol LED Arduino
    action = "on" atau "off"
    """

    if ser is None:
        return "Arduino tidak terhubung!"

    cmd = action.strip().lower()
    if cmd == "on":
        ser.write(b"ON\n")
        return "Lampu dinyalakan!"
    elif cmd == "off":
        ser.write(b"OFF\n")
        return "Lampu dimatikan!"
    else:
        return "Perintah tidak valid (gunakan 'on' atau 'off')"


# ===== TOOLS REGISTRY =====
TOOLS = {
    "calculate": calculate,
    "control_led": control_led,
}


# ===== HELPER FUNCTIONS =====
def parse_tool(response: str):
    """Extract tool call dari response"""
    if "{" not in response or "}" not in response:
        return None
    try:
        return json.loads(response)
    except:
        return None


def execute_tool(tool_call: dict):
    """Jalankan tool berdasarkan tool_call"""
    tool_name = tool_call.get("tool")
    arguments = tool_call.get("arguments", {})

    if tool_name not in TOOLS:
        return None

    try:
        return TOOLS[tool_name](**arguments)
    except:
        return None


def format_tool_result(tool_name: str, arguments: dict, result):
    """Format hasil tool untuk ditampilkan"""
    if tool_name == "calculate":
        a = arguments.get("a")
        b = arguments.get("b")
        return f"AITRI: Saya hitung dulu... {a} + {b} = {result}"

    elif tool_name == "greet":
        return f"AITRI: {result}"

    elif tool_name == "control_led":
        action = arguments.get("action", "").title()
        return f"AITRI: {result} ({action})"

    return f"AITRI: {result}"


# ===== AGENT CLASS =====
class Agent:
    """AI Agent dengan tool calling"""

    def __init__(self):
        self.messages = []

    def chat(self, user_input: str):
        """Kirim pesan ke model"""
        self.messages.append({"role": "user", "content": user_input})
        response = ollama.chat(model="aitri-agent", messages=self.messages)
        return response["message"]["content"]

    def handle_response(self, response: str):
        """Proses response dan jalankan tool jika ada"""
        tool_call = parse_tool(response)

        if not tool_call:
            return False

        result = execute_tool(tool_call)
        if result is None:
            return False

        tool_name = tool_call.get("tool")
        arguments = tool_call.get("arguments", {})

        # Tampilkan hasil
        formatted = format_tool_result(tool_name, arguments, result)
        print(formatted)

        # Update messages
        self.messages.append({"role": "assistant", "content": response})
        self.messages.append({"role": "tool", "content": str(result)})

        return True

    def run(self):
        """Main loop"""
        print("AITRI Agent siap! (ketik 'exit' untuk keluar)\n")

        while True:
            user_input = input("Kamu: ")

            if user_input.lower() in ["exit", "quit"]:
                print("Sampai jumpa!")
                break

            response = self.chat(user_input)
            print(f"DEBUG: Assistant message: {response}")

            if not self.handle_response(response):
                print(f"AITRI: {response}")
                self.messages.append({"role": "assistant", "content": response})


if __name__ == "__main__":
    agent = Agent()
    agent.run()


# ===== CARA MENAMBAH TOOLS BARU =====
"""
Untuk menambah tool baru, cukup:

1. Buat fungsi tool:
   def multiply(a: float, b: float):
       return a * b

2. Daftarkan di TOOLS:
   TOOLS = {
       "calculate": calculate,
       "greet": greet,
       "multiply": multiply,  # <-- Tambah baris ini
   }

3. (Opsional) Tambah format di format_tool_result():
   elif tool_name == "multiply":
       return f"AITRI: Hasil {a} x {b} = {result}"

Selesai! Tidak perlu ubah class Agent sama sekali.
"""
