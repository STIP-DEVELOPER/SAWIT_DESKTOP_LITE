import serial
from PyQt5.QtCore import QThread, pyqtSignal
import time

from enums.log import LogLevel, LogSource
from utils.logger import add_log


class SerialController(QThread):
    data_received = pyqtSignal(str)
    connection_lost = pyqtSignal()

    def __init__(self, port, baudrate=9600):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.ser = None
        self.is_busy = False

        self._running = False

    def run(self):
        """Start serial communication thread"""
        try:
            self._open_serial()
            self._running = True
            self._listen_loop()
        except serial.SerialException as e:
            self._handle_serial_error(e)
        finally:
            self._cleanup_serial()

    def _open_serial(self):
        """Open serial port"""
        self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
        print(f"[Serial] Connected to {self.port}")

    def _listen_loop(self):
        """Listen for incoming data and emit signals"""
        while self._running:
            self._read_serial()
            time.sleep(0.05)

    def _read_serial(self):
        """Read a single line from serial if available"""
        if self.ser and self.ser.in_waiting > 0:
            try:
                line = self.ser.read(1).decode("utf-8", "ignore")

                if not line:
                    return

                if line == "1":  # BUSY
                    self.is_busy = True
                    print("[Serial] Controller BUSY → Stop sending commands")

                elif line == "0":  # READY
                    self.is_busy = False
                    print("[Serial] Controller READY → Send enabled")

                self.data_received.emit(line)
                print(f"[Serial] - {line}")

            except Exception as e:
                print(f"[Serial] Failed to read data: {e}")
                add_log(
                    LogLevel.ERROR.value,
                    LogSource.SERIAL_CONTROLLER.value,
                    f"Serial read error: {str(e)}",
                )

    def send(self, data):
        """Send data to serial"""
        if self.ser and self.ser.is_open and not self.is_busy:
            try:
                self.ser.write((self._encode_command(data) + "\n").encode())
                print(f"[Serial] Sent: {self._encode_command(data)}")
            except Exception as e:
                print(f"[Serial] Failed to send: {e}")
                add_log(
                    LogLevel.ERROR.value,
                    LogSource.SERIAL_CONTROLLER.value,
                    f"Serial send error: {str(e)}",
                )

    def _encode_command(self, cmd: str) -> str:
        cmd = cmd.upper().strip()

        if cmd == "LEFT":
            return "L"
        elif cmd == "RIGHT":
            return "R"
        else:
            raise ValueError(f"Unknown command: {cmd}")

    def _handle_serial_error(self, error):
        """Handle serial errors and emit connection_lost"""
        print(f"[Serial] Error: {error}")
        add_log(
            LogLevel.ERROR.value,
            LogSource.SERIAL_CONTROLLER.value,
            f"{str(error)}",
        )
        self.connection_lost.emit()

    def _cleanup_serial(self):
        """Close serial port safely"""
        if self.ser and self.ser.is_open:
            self.ser.close()
            print(f"[Serial] Connection closed")

    def stop(self):
        """Stop the serial thread safely"""
        self._running = False
        self.wait()
        self._cleanup_serial()
