import serial
import time
import threading


def open_port(path, baud=115200, timeout=1):
    return serial.Serial(path, baud, timeout=timeout)


def read_frame(ser):
    """Parse single TF-Luna frame"""
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
            # else: lanjut scanning
        time.sleep(0.1)


def tfluna_reader(port_name, label):
    """Thread worker untuk membaca TF-Luna"""
    try:
        ser = open_port(port_name)
        print(f"[{label}] Listening on {port_name}")
    except Exception as e:
        print(f"[{label}] ERROR opening {port_name}: {e}")
        return

    try:
        while True:
            data = read_frame(ser)
            if data:
                print(
                    f"[{label}] Distance={data['distance_cm']} cm | Strength={data['strength']} | Temp={data['temp_c']:.2f}C"
                )
            else:
                time.sleep(0.1)

    except KeyboardInterrupt:
        pass

    finally:
        ser.close()
        print(f"[{label}] Closed")


def main():
    # Ganti dengan port TF-Luna Anda
    LEFT_PORT = "/dev/cu.usbserial-0001"
    RIGHT_PORT = "/dev/cu.usbserial-2"

    # Jalankan 2 thread
    t1 = threading.Thread(target=tfluna_reader, args=(LEFT_PORT, "LEFT"))
    t2 = threading.Thread(target=tfluna_reader, args=(RIGHT_PORT, "RIGHT"))

    t1.start()
    t2.start()

    t1.join()
    t2.join()


if __name__ == "__main__":
    main()
