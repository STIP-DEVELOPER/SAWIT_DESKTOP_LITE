from PyQt5.QtCore import QThread, pyqtSignal
import time


class LoaderThreadController(QThread):
    finished = pyqtSignal()

    def run(self):
        # Simulasi proses loading
        time.sleep(2)

        # Di sini kamu bisa load apa saja:
        # - load config
        # - detect camera
        # - load model YOLO
        # - cek serial port
        # dll.

        self.finished.emit()
