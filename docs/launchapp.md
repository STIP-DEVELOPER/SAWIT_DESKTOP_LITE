✅ LANGKAH 1 — Pastikan main.py bisa dijalankan langsung

Jalankan perintah ini:

chmod +x ~/Documents/SawitApp/src/main.py

Jika aplikasi Anda membutuhkan environment tertentu (misalnya venv), beritahu saya — nanti saya modifikasi shortcut-nya.

✅ LANGKAH 2 — Buat file .desktop

Buat file baru:

nano ~/.local/share/applications/sawitapp.desktop

Tempel isi berikut:

[Desktop Entry]
Name=Sawit App
Comment=My Sawit Python Application
Exec=python3 /home/jetson/Documents/SawitApp/src/main.py
Icon=/home/jetson/Documents/SawitApp/icon.png
Terminal=true
Type=Application
Categories=Application;

Ganti:

/home/jetson → sesuai username Jetson Anda (cek dengan whoami)

Icon=... → arahkan ke ikon PNG Anda
(kalau belum punya, nanti saya bantu buat)

Kalau Anda tidak ingin membuka terminal:

Terminal=false

✅ LANGKAH 3 — Buat shortcut muncul di Desktop

Copy .desktop ke Desktop:

cp ~/.local/share/applications/sawitapp.desktop ~/Desktop/

Lalu aktifkan permission agar bisa dieksekusi:

chmod +x ~/Desktop/sawitapp.desktop

Di Ubuntu (Gnome) biasanya perlu klik kanan → Allow Launching.
