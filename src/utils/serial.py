# import serial
# import serial.tools.list_ports


# def get_serial_ports():
#     ports = serial.tools.list_ports.comports()
#     print("found serial ports:", [p.device for p in ports])
#     return [p.device for p in ports]


import os
import serial.tools.list_ports

# Nama port tetap yang sudah kita buat lewat udev rule
FIXED_PORTS = {
    "microcontroller": "/dev/ttyMICROCONTROLLER",
    "gps": "/dev/ttyGPS",
    "lidar_left": "/dev/ttyLIDAR_LEFT",
    "lidar_right": "/dev/ttyLIDAR_RIGHT",
}


def get_serial_ports():
    """
    Fungsi ini MENGGANTIKAN fungsi lama kamu.
    Return value SAMA PERSIS: list of strings (contoh: ['/dev/ttyUSB0', '/dev/ttyACM0', ...])
    Tapi sekarang urutannya SELALU SELALU SAMA dan sesuai dengan device yang sebenarnya.
    """
    # Kumpulkan port tetap yang benar-benar ada
    active_fixed = []
    for path in FIXED_PORTS.values():
        if os.path.exists(path):
            # Ambil nama asli (ttyUSBx / ttyACM0) dari symlink
            try:
                real_path = os.readlink(path)
                full_real = os.path.join("/dev", real_path)
                active_fixed.append(full_real)
            except:
                active_fixed.append(path)  # fallback kalau symlink rusak

    # Jika semua port tetap ada → kembalikan sesuai urutan logika traktor
    if len(active_fixed) == 4:
        result = [
            FIXED_PORTS["microcontroller"],  # Arduino
            FIXED_PORTS["lidar_left"],  # TF-Luna kiri
            FIXED_PORTS["lidar_right"],  # TF-Luna kanan
            FIXED_PORTS["gps"],  # GPS u-blox
        ]
        print("found serial ports (FIXED + STABLE):", result)
        return result

    # Fallback: kalau ada yang hilang, tetap pakai cara lama (tapi beri warning)
    print(
        "Peringatan: Tidak semua port tetap terdeteksi. Gunakan scanning sementara..."
    )
    ports = serial.tools.list_ports.comports()
    result = [p.device for p in ports]
    print("found serial ports (fallback):", result)
    return result
