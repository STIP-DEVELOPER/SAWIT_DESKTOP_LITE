from PyQt5.QtCore import QThread, pyqtSignal
import serial
import time
from controller.tfluna import TFLunaController
from utils.logger import add_log
from enums.log import LogLevel, LogSource


class SerialController(QThread):
    data_received = pyqtSignal(str)
    connection_lost = pyqtSignal()
    detection_ready = pyqtSignal(str)

    def __init__(self, port, baudrate=9600, tf_luna_port=None):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.ser = None
        self.is_busy = False
        self._running = False

        self.tf_luna = TFLunaController(port=tf_luna_port)
        self.tf_luna.data_received.connect(self._update_can_send)
        self.can_send = False

    def run(self):
        """Start serial and TF-Luna threads"""
        try:
            self._open_serial()
            self._running = True
            self.tf_luna.start()
            while self._running:
                self._read_serial()
                time.sleep(0.05)
        except serial.SerialException as e:
            self._handle_serial_error(e)
        finally:
            self.tf_luna.stop()
            self._cleanup_serial()

    def _open_serial(self):
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
            msg = f"[Serial] Connected to {self.port}"
            self.detection_ready.emit(msg)
            add_log(LogLevel.INFO.value, LogSource.SERIAL_CONTROLLER.value, msg)
        except Exception as e:
            self._handle_serial_error(e)

    def _read_serial(self):
        """Read a line from Arduino if available"""
        if self.ser and self.ser.in_waiting > 0:
            try:
                line = self.ser.readline().decode(errors="ignore").strip()
                if line:
                    self.data_received.emit(line)
                    self.detection_ready.emit(f"[Serial] - {line}")
                    add_log(
                        LogLevel.INFO.value,
                        LogSource.SERIAL_CONTROLLER.value,
                        f"[Serial] - {line}",
                    )

                if "BUSY" in line.upper():
                    self.is_busy = True
                    msg = "[Serial] Arduino BUSY → Stop sending commands"
                    self.detection_ready.emit(msg)
                    add_log(
                        LogLevel.WARNING.value, LogSource.SERIAL_CONTROLLER.value, msg
                    )
                elif "READY" in line.upper():
                    self.is_busy = False
                    msg = "[Serial] Arduino READY → Send enabled"
                    self.detection_ready.emit(msg)
                    add_log(LogLevel.INFO.value, LogSource.SERIAL_CONTROLLER.value, msg)

            except Exception as e:
                err_msg = f"[Serial] Failed to read data: {e}"
                self.detection_ready.emit(err_msg)
                add_log(
                    LogLevel.ERROR.value, LogSource.SERIAL_CONTROLLER.value, err_msg
                )

    def _update_can_send(self, data):
        """Update can_send flag based on TF-Luna distance"""
        distance_m = data["distance_cm"] / 100.0
        self.can_send = distance_m <= 2.0

        msg = f"[TF-Luna] Distance: {distance_m:.2f} m → Can send: {self.can_send}"
        self.detection_ready.emit(msg)
        add_log(LogLevel.INFO.value, LogSource.SERIAL_CONTROLLER.value, msg)

    def send(self, msg: str):
        """Send message to Arduino only if allowed by TF-Luna"""
        if self.can_send and self.ser and self.ser.is_open and not self.is_busy:
            try:
                self.ser.write((msg + "\n").encode())
                msg_log = f"[Serial] Sent: {msg}"
                self.detection_ready.emit(msg_log)
                add_log(LogLevel.INFO.value, LogSource.SERIAL_CONTROLLER.value, msg_log)
            except Exception as e:
                err_msg = f"[Serial] Failed to send: {e}"
                self.detection_ready.emit(err_msg)
                add_log(
                    LogLevel.ERROR.value, LogSource.SERIAL_CONTROLLER.value, err_msg
                )
        else:
            msg = f"[Serial] Send blocked: Can send = {self.can_send}, Busy = {self.is_busy}"
            self.detection_ready.emit(msg)
            add_log(LogLevel.WARNING.value, LogSource.SERIAL_CONTROLLER.value, msg)

    def _handle_serial_error(self, error):
        err_msg = f"[Serial] Error: {error}"
        self.detection_ready.emit(err_msg)
        add_log(LogLevel.ERROR.value, LogSource.SERIAL_CONTROLLER.value, err_msg)
        self.connection_lost.emit()

    def _cleanup_serial(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
            msg = f"[Serial] Connection closed"
            self.detection_ready.emit(msg)
            add_log(LogLevel.INFO.value, LogSource.SERIAL_CONTROLLER.value, msg)

    def stop(self):
        self._running = False
        self.tf_luna.stop()
        self.wait()
        self._cleanup_serial()
