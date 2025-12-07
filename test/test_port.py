import serial.tools.list_ports


def save_device_identity():
    count = 1
    for p in serial.tools.list_ports.comports():
        print("+++++++++++++")
        print(f"{count}. PORT: {p.device}")
        print(
            f"DEVICE={p.device}| HWID={p.hwid}| LOCATION={p.location}| PID={p.pid}| VID={p.vid}"
        )
        print(p.serial_number)
        print("\n\n")
        count += 1


if __name__ == "__main__":
    save_device_identity()
