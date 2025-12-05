import serial
import time

ser = serial.Serial("/dev/cu.usbserial-1420", 9600, timeout=1)
time.sleep(2)

count = 0

last_status = ""

while count < 5:
    last_status = ser.readline().decode().strip()
    status = last_status
    print("Received:", status)
    if status == "BUSSY":
        last_status = status
        print("[SKIP] Arduino sedang sibuk, perintah tidak dikirim.\n")
        continue

    ser.write(("LEFT" + "\n").encode())
    print("Sent:", "LEFT")

    count += 1

ser.close()
