import os


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def settings_screen(cfg: dict, conn) -> None:
    while True:
        clear_screen()
        print("CONNECTION SETTINGS")
        print("-" * 40)
        print(f"1) Board#1 Port : {cfg['port_board1']}")
        print(f"2) Board#2 Port : {cfg['port_board2']}")
        print(f"3) Baudrate     : {cfg['baudrate']}")
        print("-" * 40)
        print(f"Status: {'CONNECTED' if conn.connected else 'DISCONNECTED'}")
        if conn.last_error:
            print(f"Last error: {conn.last_error}")
        print("-" * 40)
        print("C) Connect")
        print("D) Disconnect")
        print("B) Back")

        choice = input("Select: ").strip().upper()

        if choice == "1":
            cfg["port_board1"] = input("Enter Board#1 port (e.g., COM3): ").strip()
            continue
        if choice == "2":
            cfg["port_board2"] = input("Enter Board#2 port (e.g., COM4): ").strip()
            continue
        if choice == "3":
            try:
                cfg["baudrate"] = int(input("Enter baudrate (e.g., 9600): ").strip())
            except Exception:
                input("Invalid baudrate. Press Enter to continue...")
            continue
        if choice == "C":
            try:
                conn.port_board1 = cfg["port_board1"]
                conn.port_board2 = cfg["port_board2"]
                conn.baudrate = int(cfg["baudrate"])
                conn.connect()
                input("Connected. Press Enter to continue...")
            except Exception as e:
                input(f"Connect failed: {e}. Press Enter to continue...")
            continue
        if choice == "D":
            try:
                conn.close()
                input("Disconnected. Press Enter to continue...")
            except Exception as e:
                input(f"Disconnect failed: {e}. Press Enter to continue...")
            continue
        if choice == "B":
            return

        input("Invalid choice. Press Enter to continue...")
