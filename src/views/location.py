from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, pyqtSignal, QObject, QThread
import pynmea2
import serial

from configs.config_manager import ConfigManager

import requests

import time


class GPSWorker(QObject):
    position_updated = pyqtSignal(float, float)

    def __init__(self):
        super().__init__()
        self.baudrate = 9600
        self.running = True

        self.config_manager = ConfigManager()
        self.configs = self.config_manager.get_all()

        self.gps_port = self.configs.get("GPS_PORT", "")
        self.interval_minutes = self.configs.get(
            "GPS_LOG_INTERVAL_MINUTES", 30
        )  # default 30 menit

        self.last_sent_time = 0  # timestamp terakhir kirim
        self.last_lat = None
        self.last_lon = None

        print(
            f"[GPS] Port: {self.gps_port} | Kirim setiap {self.interval_minutes} menit"
        )

    def send_to_server(self):
        if not self.last_lat or not self.last_lon:
            return

        url = "https://jasaapk.us/sw/api/v1/locations"
        payload = {
            "token": "24999306-3fdb-477d-8e86-96d067cd0a60",
            "latitude": f"{self.last_lat:.6f}",
            "longitude": f"{self.last_lon:.6f}",
        }

        try:
            r = requests.post(url, json=payload, timeout=10)
            if r.status_code == 200:
                print(f"[GPS] Sukses kirim: {self.last_lat:.6f}, {self.last_lon:.6f}")
            else:
                print(f"[GPS] Gagal kirim: {r.status_code} {r.text}")
        except Exception as e:
            print(f"[GPS] Error kirim: {e}")

    def run(self):
        if not self.gps_port or self.gps_port in ["", "None"]:
            print("[GPS] Port tidak disetel ke None → GPS dimatikan")
            return

        try:
            ser = serial.Serial(self.gps_port, self.baudrate, timeout=1)
            print(f"[GPS] Terhubung ke {self.gps_port}")

            while self.running:
                line = ser.readline().decode("ascii", errors="replace").strip()
                if line.startswith(("$GPGGA", "$GNGGA", "$GPRMC", "$GNRMC")):
                    try:
                        msg = pynmea2.parse(line)
                        if msg.latitude and msg.longitude and msg.latitude != 0:
                            lat = float(msg.latitude)
                            lon = float(msg.longitude)

                            self.last_lat = lat
                            self.last_lon = lon
                            self.position_updated.emit(lat, lon)

                            # Kirim ke server sesuai interval
                            current_time = time.time()
                            if (
                                current_time - self.last_sent_time
                                >= self.interval_minutes * 60
                            ):
                                self.send_to_server()
                                self.last_sent_time = current_time
                    except:
                        continue
            ser.close()
        except Exception as e:
            print(f"[GPS] Error: {e}")

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
        if not self.gps_thread:
            self.gps_thread = QThread()
            self.gps_worker = GPSWorker()
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
