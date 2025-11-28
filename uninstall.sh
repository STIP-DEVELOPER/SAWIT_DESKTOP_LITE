#!/bin/bash

SERVICE_NAME="neo-ai.service"
INSTALL_DIR="/opt/neo_ai"
LOG_DIR="/var/log/neo_ai"

echo "=== NEO AI Uninstaller ==="

# Stop & disable service
echo "[1/4] Menghentikan service..."
sudo systemctl stop $SERVICE_NAME
sudo systemctl disable $SERVICE_NAME

# Hapus service file
echo "[2/4] Menghapus systemd service..."
sudo rm -f /etc/systemd/system/$SERVICE_NAME
sudo systemctl daemon-reload

# Hapus file aplikasi
echo "[3/4] Menghapus direktori instalasi..."
sudo rm -rf $INSTALL_DIR

# Hapus logs
echo "[4/4] Menghapus log..."
sudo rm -rf $LOG_DIR

echo "=== Uninstall selesai ==="


