#!/bin/bash

SERVICE_NAME="neo-ai.service"
INSTALL_DIR="/opt/neo_ai"
LOG_DIR="/var/log/neo_ai"

echo "=== NEO AI Installer (Tanpa Virtual Environment) ==="

# 1. Buat direktori instalasi
echo "[1/6] Membuat direktori instalasi..."
sudo mkdir -p $INSTALL_DIR

# 2. Copy semua file project ke /opt/neo_ai
echo "[2/6] Menyalin file project..."
sudo cp -r ./* $INSTALL_DIR/

# 3. Install dependencies Python global
echo "[3/6] Menginstall dependencies Python..."
sudo pip3 install -r requirements.txt

# 4. Buat direktori log
echo "[4/6] Membuat direktori log..."
sudo mkdir -p $LOG_DIR
sudo touch $LOG_DIR/app.log
sudo chmod 666 $LOG_DIR/app.log

# 5. Install Systemd service
echo "[5/6] Menginstall systemd service..."
sudo tee /etc/systemd/system/$SERVICE_NAME > /dev/null <<EOF
[Unit]
Description=NEO AI Detection System
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 $INSTALL_DIR/main.py
Restart=always
RestartSec=5
WorkingDirectory=$INSTALL_DIR
StandardOutput=append:$LOG_DIR/app.log
StandardError=append:$LOG_DIR/app.log

[Install]
WantedBy=multi-user.target
EOF

# 6. Reload dan enable service
echo "[6/6] Mengaktifkan service..."
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
sudo systemctl restart $SERVICE_NAME

echo "=== Instalasi selesai! ==="
echo "Log tersedia di: $LOG_DIR/app.log"
echo "Service: systemctl status $SERVICE_NAME"
