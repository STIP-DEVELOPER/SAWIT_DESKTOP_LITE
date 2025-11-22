import serial
import serial.tools.list_ports


def get_serial_ports():
    ports = serial.tools.list_ports.comports()
    return [p.device for p in ports]
