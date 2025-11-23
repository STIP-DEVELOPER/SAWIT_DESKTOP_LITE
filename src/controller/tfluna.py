import serial
from PyQt5.QtCore import QThread, pyqtSignal
import time
import serial.tools.list_ports

from enums.log import LogLevel, LogSource
from utils.logger import add_log


class TFLunaController(QThread):
    data_received = pyqtSignal(dict)
    connection_lost = pyqtSignal()

    def __init__(self, port: str = None, baudrate: int = 115200):
        """
        :param port: Serial port (e.g., '/dev/ttyUSB0'). Auto-detect if None.
        :param baudrate: Baudrate for TF-Luna, default 115200
        """
        super().__init__()
        self.port = port or self._find_tf_luna_port()
        if self.port is None:
            raise RuntimeError("TF-Luna not found on any serial port")
        self.baudrate = baudrate
        self.ser: serial.Serial = None
        self._running = False

    def _find_tf_luna_port(self) -> str | None:
        """Auto-detect TF-Luna port by USB/UART description"""
        ports = serial.tools.list_ports.comports()
        for p in ports:
            if "USB" in p.description or "UART" in p.description:
                return p.device
        return None

    def _open_serial(self):
        """Open serial port"""
        self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
        print(f"[TF-Luna] Connected to {self.port}")

    def _cleanup_serial(self):
        """Close serial port safely"""
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("[TF-Luna] Connection closed")

    def _read_frame(self) -> dict | None:
        """Read a single TF-Luna frame if available"""
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
        """Start the TF-Luna reading thread"""
        try:
            self._open_serial()
            self._running = True
            while self._running:
                data = self._read_frame()
                if data:
                    self.data_received.emit(data)
                    print(
                        f"[TF-Luna] Distance: {data['distance_cm']} cm | "
                        f"Strength: {data['strength']} | Temp: {data['temp_c']:.2f} C"
                    )
                else:
                    time.sleep(0.01)
        except serial.SerialException as e:
            self.connection_lost.emit()
            msg = f"[TF-Luna] Serial error: {e}"
            add_log(LogLevel.INFO.value, LogSource.TFLUNA_CONTROLLER.value, msg)

        finally:
            self._cleanup_serial()

    def stop(self):
        """Stop the thread safely"""
        self._running = False
        self.wait()
        self._cleanup_serial()
