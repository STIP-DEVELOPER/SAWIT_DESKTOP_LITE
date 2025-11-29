#!/bin/bash

echo "[1/4] Membuat shortcut desktop..."
cp SawitApp.desktop ~/.local/share/applications/
chmod +x ~/.local/share/applications/SawitApp.desktop

echo "[2/4] Menginstall systemd service..."
sudo cp sawitapp.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable sawitapp

echo "[3/4] Menjalankan service..."
sudo systemctl start sawitapp

echo "[4/4] Instalasi selesai! Aplikasi akan berjalan otomatis & fullscreen."
