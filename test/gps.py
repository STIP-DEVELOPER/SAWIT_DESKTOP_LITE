import serial
import pynmea2

ser = serial.Serial("/dev/cu.usbserial-0001", 9600, timeout=1)

while True:
    try:
        line = ser.readline().decode("ascii", errors="ignore")
        print(line)
        if line.startswith("$GPRMC"):
            msg = pynmea2.parse(line)
            print("Lat:", msg.latitude)
            print("Lon:", msg.longitude)
    except:
        pass


# import serial

# ser = serial.Serial("/dev/cu.usbserial-0001", 9600)

# while True:
#     print(ser.readline().decode(errors="ignore").strip())
