from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, pyqtSignal, QObject, QThread
import pynmea2
import serial


class GPSWorker(QObject):
    position_updated = pyqtSignal(float, float)

    def __init__(self, port="/dev/cu.usbmodem14201", baudrate=9600):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.running = True

    def run(self):
        try:
            ser = serial.Serial(self.port, baudrate=self.baudrate, timeout=1)
            while self.running:
                line = ser.readline().decode("ascii", errors="replace").strip()
                if line.startswith(("$GPGGA", "$GNGGA")):
                    msg = pynmea2.parse(line)
                    if msg.latitude and msg.latitude != 0:
                        self.position_updated.emit(msg.latitude, msg.longitude)
            ser.close()
        except Exception as e:
            print("GPS error:", e)

    def stop(self):
        self.running = False


class LocationPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.lat = -7.747888
        self.lon = 110.418756

        self.gps_thread = None
        self.gps_worker = None

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.webview = QWebEngineView()
        self.webview.setHtml(self._get_map_html(), QUrl("file://"))
        layout.addWidget(self.webview)

    def _get_map_html(self):
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
            <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
            <style>body,html{{margin:0;padding:0;height:100%;background:#111}} #map{{width:100%;height:100%}}</style>
        </head>
        <body>
            <div id="map"></div>
            <script>
                var map = L.map('map').setView([{self.lat}, {self.lon}], 18);
                L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png').addTo(map);
                var marker = L.marker([{self.lat}, {self.lon}]).addTo(map).bindPopup("Base Station").openPopup();
                var circle = L.circle([{self.lat}, {self.lon}], {{radius:50, color:'#3388ff', fillOpacity:0.2}}).addTo(map);

                function updatePosition(lat, lng) {{
                    map.setView([lat, lng], 18);
                    marker.setLatLng([lat, lng]);
                    circle.setLatLng([lat, lng]);
                }}
            </script>
        </body>
        </html>
        """

    def showEvent(self, event):
        super().showEvent(event)
        if not self.gps_thread:  # hanya buat sekali
            self.gps_thread = QThread()
            self.gps_worker = GPSWorker("/dev/cu.usbmodem14201")  # sesuaikan port
            self.gps_worker.moveToThread(self.gps_thread)

            self.gps_thread.started.connect(self.gps_worker.run)
            self.gps_worker.position_updated.connect(self.update_map)
            self.gps_thread.start()

    def hideEvent(self, event):
        super().hideEvent(event)
        if self.gps_worker:
            self.gps_worker.stop()
        if self.gps_thread:
            self.gps_thread.quit()
            self.gps_thread.wait()
            self.gps_thread = None
            self.gps_worker = None

    def update_map(self, lat, lon):
        self.lat, self.lon = lat, lon
        self.webview.page().runJavaScript(f"updatePosition({lat}, {lon})")
