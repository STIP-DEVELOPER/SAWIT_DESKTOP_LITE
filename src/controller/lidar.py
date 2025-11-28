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
        self.port = port
        # if self.port is None:
        #     raise RuntimeError("Lidar not found on any serial port")
        self.baudrate = baudrate
        self.ser: serial.Serial = None
        self._running = False

    def _open_serial(self):
        """Open serial port"""
        self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
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
            add_log(LogLevel.INFO.value, LogSource.TFLUNA_CONTROLLER.value, msg)

        finally:
            self._cleanup_serial()

    def stop(self):
        """Stop the thread safely"""
        self._running = False
        self.wait()
        self._cleanup_serial()
