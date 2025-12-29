from __future__ import annotations

import sys
from pathlib import Path

# Make sure project root is importable even if script is run from pc_app
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from uart_tools.uart_board1 import UARTBoard1
from uart_tools.uart_board2 import UARTBoard2


class RealConnection:
    def __init__(self, cfg: dict):
        self.port_board1 = cfg.get("port_board1", "COM3")
        self.port_board2 = cfg.get("port_board2", "COM4")
        self.baudrate = int(cfg.get("baudrate", 9600))

        self.connected = False
        self.last_error = ""

        self._b1: UARTBoard1 | None = None
        self._b2: UARTBoard2 | None = None

        # Cached telemetry
        self.desired_temp = None
        self.ambient_temp = None
        self.fan_speed = None

        self.current_curtain = None
        self.outdoor_temp = None
        self.outdoor_press = None
        self.light_intensity = None

        # “Desired curtain” is not separately provided by board2, keep last set value here
        self.desired_curtain = None

    def connect(self) -> None:
        try:
            self._b1 = UARTBoard1(self.port_board1, self.baudrate)
            self._b2 = UARTBoard2(self.port_board2, self.baudrate)

            self._b1.connect()
            self._b2.connect()

            self.connected = True
            self.last_error = ""
        except Exception as e:
            self.connected = False
            self.last_error = str(e)
            raise

    def close(self) -> None:
        try:
            if self._b1:
                self._b1.disconnect()
            if self._b2:
                self._b2.disconnect()
        finally:
            self.connected = False

    def update(self) -> None:
        if not self.connected:
            return

        try:
            # Board1 temps come as integral + fractional (tenths)
            d_i = self._b1.get_desired_temp_integral()
            d_f = self._b1.get_desired_temp_fractional()
            a_i = self._b1.get_ambient_temp_integral()
            a_f = self._b1.get_ambient_temp_fractional()
            fan = self._b1.get_fan_speed()

            if None not in (d_i, d_f):
                self.desired_temp = float(d_i) + float(d_f) / 10.0
            if None not in (a_i, a_f):
                self.ambient_temp = float(a_i) + float(a_f) / 10.0
            if fan is not None:
                self.fan_speed = float(fan)

            # Board2
            cur = self._b2.get_curtain_status()
            ot = self._b2.get_outdoor_temp()
            op = self._b2.get_outdoor_pressure()
            li = self._b2.get_light_intensity()

            if cur is not None:
                self.current_curtain = float(cur)
                if self.desired_curtain is None:
                    self.desired_curtain = float(cur)
            if ot is not None:
                self.outdoor_temp = float(ot)
            if op is not None:
                self.outdoor_press = float(op)
            if li is not None:
                self.light_intensity = int(li)

            self.last_error = ""
        except Exception as e:
            self.last_error = str(e)
            # Do not crash UI; keep last known values


class RealAircon:
    def __init__(self, conn: RealConnection):
        self._c = conn

    def getDesiredTemp(self):
        return self._c.desired_temp

    def getAmbientTemp(self):
        return self._c.ambient_temp

    def getFanSpeed(self):
        return self._c.fan_speed

    def setDesiredTemp(self, temp: float):
        if not self._c.connected or self._c._b1 is None:
            raise RuntimeError("Not connected (Board1).")
        ok = self._c._b1.set_desired_temp(float(temp))
        self._c.desired_temp = float(temp) if ok else self._c.desired_temp
        return ok


class RealCurtain:
    def __init__(self, conn: RealConnection):
        self._c = conn

    def getDesiredCurtain(self):
        return self._c.desired_curtain

    def getCurrentCurtain(self):
        return self._c.current_curtain

    def getOutdoorTemp(self):
        return self._c.outdoor_temp

    def getOutdoorPress(self):
        return self._c.outdoor_press

    def getLightIntensity(self):
        return self._c.light_intensity

    def setDesiredCurtain(self, val: int):
        if not self._c.connected or self._c._b2 is None:
            raise RuntimeError("Not connected (Board2).")
        v = float(val)
        ok = self._c._b2.set_curtain_status(v)
        if ok:
            self._c.desired_curtain = v
        return ok


def build_real_system(cfg: dict) -> dict:
    conn = RealConnection(cfg)
    aircon = RealAircon(conn)
    curtain = RealCurtain(conn)
    return {"conn": conn, "aircon": aircon, "curtain": curtain}
