#!/bin/bash

echo "Menghapus service..."
sudo systemctl stop sawitapp
sudo systemctl disable sawitapp
sudo rm -f /etc/systemd/system/sawitapp.service
sudo systemctl daemon-reload

echo "Menghapus shortcut..."
rm -f ~/.local/share/applications/SawitApp.desktop

echo "Uninstall selesai."
