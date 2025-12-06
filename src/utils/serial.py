# import serial
# import serial.tools.list_ports


# def get_serial_ports():
#     ports = serial.tools.list_ports.comports()
#     print("found serial ports:", [p.device for p in ports])
#     return [p.device for p in ports]


import os
import platform

# Nama port custom (ubah sesuai sistem kamu)
if platform.system() == "Linux":
    FIXED_PORTS = {
        "microcontroller": "/dev/ttyMICROCONTROLLER",
        "lidar_left": "/dev/ttyLIDAR_LEFT",
        "lidar_right": "/dev/ttyLIDAR_RIGHT",
        "gps": "/dev/ttyGPS",
    }
elif platform.system() == "Darwin":  # macOS
    FIXED_PORTS = {
        "microcontroller": "/dev/cu.usbserial-0001",  # sesuaikan
        "lidar_left": "/dev/cu.usbmodem14301",  # sesuaikan
        "lidar_right": "/dev/cu.usbmodem14302",  # sesuaikan
        "gps": "/dev/cu.usbserial-0002",  # sesuaikan
    }
else:  # Windows
    FIXED_PORTS = {
        "microcontroller": "COM3",
        "lidar_left": "COM4",
        "lidar_right": "COM5",
        "gps": "COM6",
    }


def get_serial_ports():
    """
    Return list string PERSIS seperti fungsi lama kamu,
    tapi sekarang pakai nama custom yang stabil.
    """
    ports = []
    order = ["microcontroller", "lidar_left", "lidar_right", "gps"]

    for key in order:
        path = FIXED_PORTS[key]
        if os.path.exists(path) or platform.system() == "Windows":
            ports.append(path)

    if len(ports) == 4:
        print("found serial ports (CUSTOM):", ports)
        return ports

    # Fallback kalau di macOS/Windows belum diatur
    try:
        import serial.tools.list_ports

        fallback = [p.device for p in serial.tools.list_ports.comports()]
        print("found serial ports (fallback):", fallback)
        return fallback
    except:
        return ports


# Tes langsung
if __name__ == "__main__":
    print(get_serial_ports())
