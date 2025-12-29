import os


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def parse_percent(s: str) -> int:
    val = int(s.strip())
    if not (0 <= val <= 100):
        raise ValueError("Curtain must be between 0 and 100")
    return val


def curtain_screen(cfg: dict, conn, curtain) -> None:
    while True:
        clear_screen()
        print("CURTAIN CONTROL")
        print("-" * 40)
        print(f"Ports: B1={cfg['port_board1']} B2={cfg['port_board2']} | Baud={cfg['baudrate']}")
        print(f"Status: {'CONNECTED' if conn.connected else 'DISCONNECTED'}")
        if conn.last_error:
            print(f"Last error: {conn.last_error}")
        print("-" * 40)

        if conn.connected:
            try:
                conn.update()
                desired = curtain.getDesiredCurtain()
                current = curtain.getCurrentCurtain()
                ot = curtain.getOutdoorTemp()
                op = curtain.getOutdoorPress()
                li = curtain.getLightIntensity()
                print(f"Desired Curtain : {desired}%" if desired is not None else "Desired Curtain : -")
                print(f"Current Curtain : {current}%" if current is not None else "Current Curtain : -")
                print(f"Outdoor Temp    : {ot:.1f} C" if ot is not None else "Outdoor Temp    : -")
                print(f"Outdoor Press   : {op:.1f} hPa" if op is not None else "Outdoor Press   : -")
                print(f"Light Intensity : {li}%" if li is not None else "Light Intensity : -")
                if li is not None and li < 25:
                    print("NOTE: Auto-close active (dark environment).")
            except Exception as e:
                print(f"Read error: {e}")
        else:
            print("Not connected. Go to Settings to connect.")

        print("-" * 40)
        print("S) Set desired curtain (%)")
        print("R) Refresh")
        print("L) Toggle low light (mock demo)")
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
            raw = input("Enter desired curtain (0-100): ")
            try:
                val = parse_percent(raw)
                curtain.setDesiredCurtain(val)
                input(f"Set to {val}%. Press Enter to continue...")
            except Exception as e:
                input(f"Invalid input: {e}. Press Enter to continue...")
            continue

        if cmd == "L":
            # MOCK DEMO: force light intensity to show auto-close behavior.
            if not conn.connected:
                input("Not connected. Press Enter to continue...")
                continue

            try:
                current_li = curtain.getLightIntensity()
                new_li = 10 if current_li >= 25 else 64  # 10 -> dark, 64 -> normal

                # This works with the mock backend (it has conn.light_intensity).
                if hasattr(conn, "light_intensity"):
                    conn.light_intensity = new_li

                    # Make auto-close effect immediate in the mock
                    if new_li < 25 and hasattr(conn, "desired_curtain"):
                        conn.desired_curtain = 100

                input(f"Light intensity set to {new_li}% (mock). Press Enter to continue...")
            except Exception as e:
                input(f"Mock demo failed: {e}. Press Enter to continue...")

            continue

        input("Invalid choice. Press Enter to continue...")
