import os

from app_state import load_config, save_config
from system_factory import build_system
from ui_aircon import aircon_screen
from ui_curtain import curtain_screen
from ui_settings import settings_screen


def clear_screen() -> None:
    # Clear the console screen (Windows/macOS/Linux)
    os.system("cls" if os.name == "nt" else "clear")


def main() -> None:
    # Entry point for the BM-3 UI application.
    cfg = load_config()

    # System (mock or real based on config)
    system = build_system(cfg)
    conn = system["conn"]
    aircon = system["aircon"]
    curtain = system["curtain"]

    while True:
        clear_screen()
        print("HOME AUTOMATION - MAIN MENU")
        print("-" * 40)
        print(f"Board#1 Port: {cfg['port_board1']} | Board#2 Port: {cfg['port_board2']} | Baud: {cfg['baudrate']}")
        print(f"Status: {'CONNECTED' if conn.connected else 'DISCONNECTED'}")
        if conn.last_error:
            print(f"Last error: {conn.last_error}")
        print("-" * 40)
        print("1) Air Conditioner")
        print("2) Curtain Control")
        print("3) Connection Settings")
        print("0) Exit")
        choice = input("Select: ").strip()

        if choice == "1":
            aircon_screen(cfg, conn, aircon)
        elif choice == "2":
            curtain_screen(cfg, conn, curtain)
        elif choice == "3":
            settings_screen(cfg, conn)
            save_config(cfg)
        elif choice == "0":
            try:
                conn.close()
            except Exception:
                pass
            print("Bye.")
            return
        else:
            input("Invalid choice. Press Enter to continue...")


if __name__ == "__main__":
    main()
