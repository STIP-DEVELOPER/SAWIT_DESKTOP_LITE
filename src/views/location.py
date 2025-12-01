import sys
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl


class LocationPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # title = QLabel("Lokasi Base Station")
        # title.setStyleSheet("color: #ccc; font-size: 16px; font-weight: bold;")
        # layout.addWidget(title)

        self.webview = QWebEngineView()
        self.webview.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.webview.setHtml(self._get_map_html(), QUrl("file://"))
        layout.addWidget(self.webview)

        self.setLayout(layout)

    def _get_map_html(self):
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
            <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
            <style>
                body, html { margin:0; padding:0; height:100%; background:#111; }
                #map { width:100%; height:100%; }
            </style>
        </head>
        <body>
            <div id="map"></div>
            <script>
                const lat = -7.747887983988562;
                const lng = 110.41875559563437;

                const map = L.map('map').setView([lat, lng], 17);

                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    attribution: '&copy; OpenStreetMap contributors'
                }).addTo(map);

                L.marker([lat, lng])
                    .addTo(map)
                    .bindPopup("<b>Base Station</b><br>Lokasi tetap aplikasi")
                    .openPopup();

                L.circle([lat, lng], {
                    color: '#3388ff',
                    fillColor: '#3388ff',
                    fillOpacity: 0.2,
                    radius: 100
                }).addTo(map);
            </script>
        </body>
        </html>
        """
