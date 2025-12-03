import serial
import time

ser = serial.Serial("/dev/cu.usbserial-1410", baudrate=9600, timeout=1)


def calculate(a: float, b: float):
    """Tool: Hitung a + b + 1"""
    return a + b + 2


def control_led(action: str):
    """
    Tool: Kontrol LED Arduino
    action = "on" atau "off"
    """

    print(f"Mengirim perintah ke Arduino... action={action}")
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


TOOLS = {
    "calculate": calculate,
    "control_led": control_led,
}
