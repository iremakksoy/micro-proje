import os


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def parse_temp(s: str) -> float:
    # Accepts '29.5' or '29,5'. Returns float rounded to 1 decimal.
    s = s.strip().replace(",", ".")
    val = float(s)
    val = round(val, 1)
    if not (10.0 <= val <= 50.0):
        raise ValueError("Temperature must be between 10.0 and 50.0")
    return val


def aircon_screen(cfg: dict, conn, aircon) -> None:
    while True:
        clear_screen()
        print("AIR CONDITIONER")
        print("-" * 40)
        print(f"Ports: B1={cfg['port_board1']} B2={cfg['port_board2']} | Baud={cfg['baudrate']}")
        print(f"Status: {'CONNECTED' if conn.connected else 'DISCONNECTED'}")
        if conn.last_error:
            print(f"Last error: {conn.last_error}")
        print("-" * 40)

        if conn.connected:
            try:
                conn.update()
                desired = aircon.getDesiredTemp()
                ambient = aircon.getAmbientTemp()
                fan = aircon.getFanSpeed()
                print(f"Desired Temp : {desired:.1f} C")
                print(f"Ambient Temp : {ambient:.1f} C")
                print(f"Fan Speed    : {fan:.1f} rps")
            except Exception as e:
                print(f"Read error: {e}")
        else:
            print("Not connected. Go to Settings to connect.")

        print("-" * 40)
        print("S) Set desired temperature")
        print("R) Refresh")
        print("B) Back")
        cmd = input("Select: ").strip().upper()

        if cmd == "B":
            return
        if cmd == "R":
            continue
        if cmd == "S":
            if not conn.connected:
                input("Not connected. Press Enter to continue...")
                continue
            raw = input("Enter desired temp (10.0 - 50.0): ")
            try:
                val = parse_temp(raw)
                aircon.setDesiredTemp(val)
                input(f"Set to {val:.1f} C. Press Enter to continue...")
            except Exception as e:
                input(f"Invalid input: {e}. Press Enter to continue...")
            continue

        input("Invalid choice. Press Enter to continue...")
