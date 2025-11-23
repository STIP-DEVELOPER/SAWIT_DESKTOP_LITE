import serial
import time

# Ganti sesuai port USB Raspberry Pi 5
ser = serial.Serial("/dev/cu.usbserial-0001", 115200, timeout=1)


def read_tf_luna():
    while True:
        data = ser.read(9)
        if len(data) == 9:
            if data[0] == 0x59 and data[1] == 0x59:
                dist = data[2] + data[3] * 256
                strength = data[4] + data[5] * 256
                temp = (data[6] + data[7] * 256) / 8 - 256
                print(f"Distance: {dist} cm, Strength: {strength}, Temp: {temp:.2f} °C")
        time.sleep(0.1)


if __name__ == "__main__":
    try:
        read_tf_luna()
    except KeyboardInterrupt:
        ser.close()
        print("Stopped")
