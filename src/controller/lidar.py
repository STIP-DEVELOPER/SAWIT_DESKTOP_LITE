import serial
from PyQt5.QtCore import QThread, pyqtSignal
import time

from enums.log import LogLevel, LogSource
from utils.logger import add_log


class LidarController(QThread):
    data_received = pyqtSignal(dict)
    connection_lost = pyqtSignal()

    def __init__(self, port: str = None, baudrate: int = 115200):
        """
        :param port: Serial port (e.g., '/dev/ttyUSB0'). Auto-detect if None.
        :param baudrate: Baudrate for Lidar, default 115200
        """
        super().__init__()
        print("[Lidar] Initializing LidarController")
        self.port = port
        if self.port is None:
            print(f"[Lidar] No port specified, auto-detection not implemented.")
        else:
            print(f"[Lidar] Using specified port: {self.port}")
        self.baudrate = baudrate
        self.ser: serial.Serial = None
        self._running = False

    def _open_serial(self):
        """Open serial port"""
        self.ser = serial.Serial(self.port, self.baudrate, timeout=0.05)
        print(f"[Lidar] Connected to {self.port}")

    def _cleanup_serial(self):
        """Close serial port safely"""
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("[Lidar] Connection closed")

    def _read_frame(self) -> dict | None:
        """Read a single Lidar frame if available"""
        if not self.ser:
            return None

        while True:
            b1 = self.ser.read(1)
            if not b1:
                return None
            if b1 == b"\x59":
                b2 = self.ser.read(1)
                if b2 == b"\x59":
                    frame = self.ser.read(7)
                    if len(frame) != 7:
                        return None
                    dist = frame[0] + frame[1] * 256
                    strength = frame[2] + frame[3] * 256
                    temp_raw = frame[4] + frame[5] * 256
                    temp = temp_raw / 8.0 - 256
                    return {"distance_cm": dist, "strength": strength, "temp_c": temp}
                else:
                    continue

    def run(self):
        """Start the Lidar reading thread"""
        print(f"[Lidar] Starting LidarController thread on port {self.port}")
        try:
            self._open_serial()
            self._running = True
            while self._running:
                data = self._read_frame()
                if data:
                    self.data_received.emit(data)
                else:
                    time.sleep(0.01)
        except serial.SerialException as e:
            self.connection_lost.emit()
            msg = f"[Lidar] Serial error: {e}"
            add_log(LogLevel.INFO.value, LogSource.LIDAR_CONTROLLER.value, msg)

        finally:
            self._cleanup_serial()

    def stop(self):
        self._running = False
        print("[Lidar] Stop requested")

        try:
            if self.ser:
                self.ser.cancel_read()
        except:
            pass

        self.wait(500)  # Wait for thread to finish
        self._cleanup_serial()
