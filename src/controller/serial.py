import serial
from PyQt5.QtCore import QThread, pyqtSignal
import time


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
                line = self.ser.readline().decode(errors="ignore").strip()
                if line:
                    self.data_received.emit(line)
                    print(f"[Serial] - {line}")

                if "BUSY" in line.upper():
                    self.is_busy = True
                    print("[Serial] Arduino BUSY → Stop sending commands")

                elif "READY" in line.upper():
                    self.is_busy = False
                    print("[Serial] Arduino READY → Send enabled")

            except Exception as e:
                print(f"[Serial] Failed to read data: {e}")

    def send(self, data):
        """Send data to serial"""
        if self.ser and self.ser.is_open:
            try:
                self.ser.write((data + "\n").encode())
                print(f"[Serial] Sent: {data}")
            except Exception as e:
                print(f"[Serial] Failed to send: {e}")

    def _handle_serial_error(self, error):
        """Handle serial errors and emit connection_lost"""
        print(f"[Serial] Error: {error}")
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
