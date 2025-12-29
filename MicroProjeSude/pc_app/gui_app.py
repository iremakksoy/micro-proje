import tkinter as tk
from tkinter import ttk, messagebox

from app_state import load_config, save_config
from system_factory import build_system


def fmt_float(x, nd=1):
    try:
        return f"{float(x):.{nd}f}"
    except Exception:
        return "-"


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Home Automation (BM-3 UI)")
        self.geometry("860x520")

        self.cfg = load_config()

        # Backend (mock or real based on config)
        self.system = build_system(self.cfg)
        self.conn = self.system["conn"]
        self.aircon = self.system["aircon"]
        self.curtain = self.system["curtain"]

        # UI state
        self.var_status = tk.StringVar(value="DISCONNECTED")
        self.var_ports = tk.StringVar(value=self._ports_text())
        self.var_error = tk.StringVar(value="")
        self.auto_refresh = tk.BooleanVar(value=False)
        self.refresh_ms = tk.IntVar(value=int(self.cfg.get("refresh_interval_ms", 500)))

        # Air values
        self.var_desired_t = tk.StringVar(value="-")
        self.var_ambient_t = tk.StringVar(value="-")
        self.var_fan = tk.StringVar(value="-")

        # Curtain values
        self.var_desired_c = tk.StringVar(value="-")
        self.var_current_c = tk.StringVar(value="-")
        self.var_out_t = tk.StringVar(value="-")
        self.var_out_p = tk.StringVar(value="-")
        self.var_light = tk.StringVar(value="-")
        self.var_autoclose = tk.StringVar(value="-")

        self._build_ui()

    def _ports_text(self) -> str:
        return f"B1={self.cfg['port_board1']}  B2={self.cfg['port_board2']}  Baud={self.cfg['baudrate']}"

    def _build_ui(self):
        # Top status bar
        top = ttk.Frame(self, padding=10)
        top.pack(fill="x")

        ttk.Label(top, textvariable=self.var_ports).pack(side="left")
        ttk.Label(top, text="   |   ").pack(side="left")
        ttk.Label(top, text="Status:").pack(side="left")
        ttk.Label(top, textvariable=self.var_status).pack(side="left")

        ttk.Label(top, text="   |   Error:").pack(side="left")
        ttk.Label(top, textvariable=self.var_error).pack(side="left", padx=(0, 10))

        ttk.Button(top, text="Refresh", command=self.refresh).pack(side="right")
        ttk.Checkbutton(top, text="Auto refresh", variable=self.auto_refresh,
                        command=self._auto_refresh_loop).pack(side="right", padx=10)

        # Tabs
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_dashboard = ttk.Frame(self.tabs, padding=10)
        self.tab_air = ttk.Frame(self.tabs, padding=10)
        self.tab_curtain = ttk.Frame(self.tabs, padding=10)
        self.tab_settings = ttk.Frame(self.tabs, padding=10)

        self.tabs.add(self.tab_dashboard, text="Dashboard")
        self.tabs.add(self.tab_air, text="Air Conditioner")
        self.tabs.add(self.tab_curtain, text="Curtain Control")
        self.tabs.add(self.tab_settings, text="Settings")

        self._build_dashboard()
        self._build_air()
        self._build_curtain()
        self._build_settings()

    def _build_dashboard(self):
        grid = ttk.Frame(self.tab_dashboard)
        grid.pack(fill="both", expand=True)

        air_card = ttk.LabelFrame(grid, text="Air Conditioner Summary", padding=10)
        cur_card = ttk.LabelFrame(grid, text="Curtain Summary", padding=10)

        air_card.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        cur_card.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)
        grid.rowconfigure(0, weight=1)

        # Air summary
        ttk.Label(air_card, text="Desired Temp (C):").grid(row=0, column=0, sticky="w")
        ttk.Label(air_card, textvariable=self.var_desired_t).grid(row=0, column=1, sticky="w")
        ttk.Label(air_card, text="Ambient Temp (C):").grid(row=1, column=0, sticky="w")
        ttk.Label(air_card, textvariable=self.var_ambient_t).grid(row=1, column=1, sticky="w")
        ttk.Label(air_card, text="Fan Speed (rps):").grid(row=2, column=0, sticky="w")
        ttk.Label(air_card, textvariable=self.var_fan).grid(row=2, column=1, sticky="w")

        ttk.Button(air_card, text="Open Air Conditioner", command=lambda: self.tabs.select(self.tab_air))\
            .grid(row=3, column=0, columnspan=2, pady=(10, 0), sticky="ew")

        # Curtain summary
        ttk.Label(cur_card, text="Desired Curtain (%):").grid(row=0, column=0, sticky="w")
        ttk.Label(cur_card, textvariable=self.var_desired_c).grid(row=0, column=1, sticky="w")
        ttk.Label(cur_card, text="Current Curtain (%):").grid(row=1, column=0, sticky="w")
        ttk.Label(cur_card, textvariable=self.var_current_c).grid(row=1, column=1, sticky="w")
        ttk.Label(cur_card, text="Light (%):").grid(row=2, column=0, sticky="w")
        ttk.Label(cur_card, textvariable=self.var_light).grid(row=2, column=1, sticky="w")
        ttk.Label(cur_card, text="Auto-close:").grid(row=3, column=0, sticky="w")
        ttk.Label(cur_card, textvariable=self.var_autoclose).grid(row=3, column=1, sticky="w")

        ttk.Button(cur_card, text="Open Curtain Control", command=lambda: self.tabs.select(self.tab_curtain))\
            .grid(row=4, column=0, columnspan=2, pady=(10, 0), sticky="ew")

    def _build_air(self):
        left = ttk.LabelFrame(self.tab_air, text="Telemetry", padding=10)
        right = ttk.LabelFrame(self.tab_air, text="Control", padding=10)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))
        right.pack(side="right", fill="y")

        ttk.Label(left, text="Desired Temp (C):").grid(row=0, column=0, sticky="w")
        ttk.Label(left, textvariable=self.var_desired_t).grid(row=0, column=1, sticky="w")
        ttk.Label(left, text="Ambient Temp (C):").grid(row=1, column=0, sticky="w")
        ttk.Label(left, textvariable=self.var_ambient_t).grid(row=1, column=1, sticky="w")
        ttk.Label(left, text="Fan Speed (rps):").grid(row=2, column=0, sticky="w")
        ttk.Label(left, textvariable=self.var_fan).grid(row=2, column=1, sticky="w")

        ttk.Label(right, text="Set Desired Temp (10.0 - 50.0)").pack(anchor="w")
        self.entry_temp = ttk.Entry(right)
        self.entry_temp.pack(fill="x", pady=5)
        ttk.Button(right, text="Set", command=self.set_desired_temp).pack(fill="x")
        ttk.Button(right, text="Refresh", command=self.refresh).pack(fill="x", pady=(8, 0))

    def _build_curtain(self):
        left = ttk.LabelFrame(self.tab_curtain, text="Telemetry", padding=10)
        right = ttk.LabelFrame(self.tab_curtain, text="Control", padding=10)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))
        right.pack(side="right", fill="y")

        rows = [
            ("Desired Curtain (%)", self.var_desired_c),
            ("Current Curtain (%)", self.var_current_c),
            ("Outdoor Temp (C)", self.var_out_t),
            ("Outdoor Press (hPa)", self.var_out_p),
            ("Light Intensity (%)", self.var_light),
            ("Auto-close", self.var_autoclose),
        ]
        for i, (label, var) in enumerate(rows):
            ttk.Label(left, text=label + ":").grid(row=i, column=0, sticky="w")
            ttk.Label(left, textvariable=var).grid(row=i, column=1, sticky="w")

        ttk.Label(right, text="Set Desired Curtain (0 - 100)").pack(anchor="w")
        self.entry_curtain = ttk.Entry(right)
        self.entry_curtain.pack(fill="x", pady=5)
        ttk.Button(right, text="Set", command=self.set_desired_curtain).pack(fill="x")
        ttk.Button(right, text="Refresh", command=self.refresh).pack(fill="x", pady=(8, 0))

        # Mock demo button (optional)
        ttk.Separator(right).pack(fill="x", pady=10)
        ttk.Button(right, text="Mock: Toggle Low Light", command=self.toggle_low_light).pack(fill="x")

    def _build_settings(self):
        frm = ttk.Frame(self.tab_settings)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="Board#1 Port").grid(row=0, column=0, sticky="w")
        self.entry_b1 = ttk.Entry(frm)
        self.entry_b1.insert(0, self.cfg["port_board1"])
        self.entry_b1.grid(row=0, column=1, sticky="ew", padx=10)

        ttk.Label(frm, text="Board#2 Port").grid(row=1, column=0, sticky="w")
        self.entry_b2 = ttk.Entry(frm)
        self.entry_b2.insert(0, self.cfg["port_board2"])
        self.entry_b2.grid(row=1, column=1, sticky="ew", padx=10)

        ttk.Label(frm, text="Baudrate").grid(row=2, column=0, sticky="w")
        self.entry_baud = ttk.Entry(frm)
        self.entry_baud.insert(0, str(self.cfg["baudrate"]))
        self.entry_baud.grid(row=2, column=1, sticky="ew", padx=10)

        ttk.Label(frm, text="Auto refresh (ms)").grid(row=3, column=0, sticky="w")
        self.entry_ms = ttk.Entry(frm)
        self.entry_ms.insert(0, str(self.refresh_ms.get()))
        self.entry_ms.grid(row=3, column=1, sticky="ew", padx=10)

        frm.columnconfigure(1, weight=1)

        btns = ttk.Frame(frm)
        btns.grid(row=4, column=0, columnspan=2, sticky="ew", pady=15)

        ttk.Button(btns, text="Apply Settings", command=self.apply_settings).pack(side="left")
        ttk.Button(btns, text="Connect", command=self.connect).pack(side="left", padx=10)
        ttk.Button(btns, text="Disconnect", command=self.disconnect).pack(side="left")

    # -------- Actions --------

    def apply_settings(self):
        self.cfg["port_board1"] = self.entry_b1.get().strip()
        self.cfg["port_board2"] = self.entry_b2.get().strip()
        try:
            self.cfg["baudrate"] = int(self.entry_baud.get().strip())
        except Exception:
            messagebox.showerror("Invalid baudrate", "Baudrate must be an integer.")
            return
        try:
            self.refresh_ms.set(int(self.entry_ms.get().strip()))
        except Exception:
            messagebox.showerror("Invalid refresh", "Refresh interval must be an integer (ms).")
            return

        save_config(self.cfg)
        self.var_ports.set(self._ports_text())
        messagebox.showinfo("Saved", "Settings saved to config.json")

    def connect(self):
        try:
            # Mock connect
            self.conn.port_board1 = self.cfg["port_board1"]
            self.conn.port_board2 = self.cfg["port_board2"]
            self.conn.baudrate = int(self.cfg["baudrate"])
            self.conn.connect()
            self.var_status.set("CONNECTED")
            self.var_error.set("")
            self.refresh()
        except Exception as e:
            self.var_error.set(str(e))
            messagebox.showerror("Connect failed", str(e))

    def disconnect(self):
        try:
            self.conn.close()
            self.var_status.set("DISCONNECTED")
            self.var_error.set("")
        except Exception as e:
            self.var_error.set(str(e))
            messagebox.showerror("Disconnect failed", str(e))

    def refresh(self):
        if not getattr(self.conn, "connected", False):
            self.var_status.set("DISCONNECTED")
            return

        try:
            self.conn.update()

            # Air
            self.var_desired_t.set(fmt_float(self.aircon.getDesiredTemp(), 1))
            self.var_ambient_t.set(fmt_float(self.aircon.getAmbientTemp(), 1))
            self.var_fan.set(fmt_float(self.aircon.getFanSpeed(), 1))

            # Curtain
            self.var_desired_c.set(str(self.curtain.getDesiredCurtain()))
            self.var_current_c.set(str(self.curtain.getCurrentCurtain()))
            self.var_out_t.set(fmt_float(self.curtain.getOutdoorTemp(), 1))
            self.var_out_p.set(fmt_float(self.curtain.getOutdoorPress(), 1))
            li = self.curtain.getLightIntensity()
            self.var_light.set(str(li))
            self.var_autoclose.set("ACTIVE" if int(li) < 25 else "OFF")

            self.var_status.set("CONNECTED")
            self.var_error.set("")
        except Exception as e:
            self.var_error.set(str(e))
            self.var_status.set("CONNECTED")  # still connected but last op failed

    def set_desired_temp(self):
        if not getattr(self.conn, "connected", False):
            messagebox.showwarning("Not connected", "Connect first.")
            return

        raw = self.entry_temp.get().strip().replace(",", ".")
        try:
            val = round(float(raw), 1)
            if not (10.0 <= val <= 50.0):
                raise ValueError("Temperature must be between 10.0 and 50.0")
            self.aircon.setDesiredTemp(val)
            self.refresh()
        except Exception as e:
            messagebox.showerror("Invalid input", str(e))

    def set_desired_curtain(self):
        if not getattr(self.conn, "connected", False):
            messagebox.showwarning("Not connected", "Connect first.")
            return

        raw = self.entry_curtain.get().strip()
        try:
            val = int(raw)
            if not (0 <= val <= 100):
                raise ValueError("Curtain must be between 0 and 100")
            self.curtain.setDesiredCurtain(val)
            self.refresh()
        except Exception as e:
            messagebox.showerror("Invalid input", str(e))

    def toggle_low_light(self):
        # Mock-only demo: force light intensity low/high
        if not getattr(self.conn, "connected", False):
            messagebox.showwarning("Not connected", "Connect first.")
            return
        if hasattr(self.conn, "light_intensity"):
            li = int(getattr(self.conn, "light_intensity"))
            new_li = 10 if li >= 25 else 64
            self.conn.light_intensity = new_li
            if new_li < 25 and hasattr(self.conn, "desired_curtain"):
                self.conn.desired_curtain = 100
            self.refresh()

    def _auto_refresh_loop(self):
        if self.auto_refresh.get():
            try:
                interval = int(self.refresh_ms.get())
                interval = max(100, interval)
            except Exception:
                interval = 500
            self.refresh()
            self.after(interval, self._auto_refresh_loop)


if __name__ == "__main__":
    App().mainloop()
