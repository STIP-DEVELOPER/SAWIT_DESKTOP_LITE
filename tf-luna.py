import serial
import time


def open_port(path="/dev/cu.usbserial-0001", baud=115200, timeout=1):
    return serial.Serial(path, baud, timeout=timeout)


def read_frame(ser):
    # Cari header 0x59 0x59
    while True:
        b = ser.read(1)
        if not b:
            return None
        if b == b"\x59":
            b2 = ser.read(1)
            if b2 == b"\x59":
                frame = ser.read(7)
                if len(frame) != 7:
                    return None
                dist = frame[0] + frame[1] * 256
                strength = frame[2] + frame[3] * 256
                temp_raw = frame[4] + frame[5] * 256
                temp = temp_raw / 8.0 - 256
                return {"distance_cm": dist, "strength": strength, "temp_c": temp}
            else:
                # continue scanning
                continue


def main():
    ser = open_port("/dev/cu.usbserial-0001", 115200, timeout=1)
    print("Listening TF-Luna on", ser.port)
    try:
        while True:
            data = read_frame(ser)
            if data:
                print(
                    f"Distance: {data['distance_cm']} cm | Strength: {data['strength']} | Temp: {data['temp_c']:.2f} C"
                )
            else:
                # timeout or bad frame - try again
                time.sleep(0.01)
    except KeyboardInterrupt:
        ser.close()
        print("Closed.")


if __name__ == "__main__":
    main()
