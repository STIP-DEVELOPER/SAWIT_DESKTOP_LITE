import serial
import serial.tools.list_ports


def get_serial_ports():
    ports = serial.tools.list_ports.comports()
    print("found serial ports:", [p.device for p in ports])
    return [p.device for p in ports]
