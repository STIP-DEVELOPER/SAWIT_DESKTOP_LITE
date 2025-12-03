import serial
import pynmea2

ser = serial.Serial("/dev/cu.usbmodem14201", baudrate=9600, timeout=1)

while True:
    line = ser.readline().decode("ascii", errors="replace").strip()
    if line.startswith("$GPGGA") or line.startswith("$GNGGA"):
        msg = pynmea2.parse(line)
        if msg.latitude and msg.latitude != 0:
            print(f"Lat: {msg.latitude:.6f}, Lon: {msg.longitude:.6f}")
        else:
            print("Menunggu fix GPS...")
