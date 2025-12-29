import random
import time
from typing import Dict


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


class HomeAutomationSystemConnectionMock:
    # Mock connection that simulates two boards (Board#1 + Board#2)

    def __init__(self, port_board1: str, port_board2: str, baudrate: int):
        self.port_board1 = port_board1
        self.port_board2 = port_board2
        self.baudrate = baudrate

        self.connected = False
        self.last_error = ""

        # Board #1 (air conditioner)
        self.desired_temp = 24.0
        self.ambient_temp = 23.4
        self.fan_speed = 8.0  # rps

        # Board #2 (curtain + outdoor)
        self.desired_curtain = 50  # %
        self.current_curtain = 40  # %
        self.outdoor_temp = 12.7
        self.outdoor_press = 1013.2  # hPa
        self.light_intensity = 65  # 0..100 %

        self._last_update = time.time()

    def connect(self) -> None:
        self.connected = True
        self.last_error = ""

    def close(self) -> None:
        self.connected = False

    def update(self) -> None:
        if not self.connected:
            self.last_error = "Not connected"
            raise RuntimeError("Not connected")

        now = time.time()
        dt = now - self._last_update
        self._last_update = now

        # Ambient temperature slowly approaches desired temperature
        diff = self.desired_temp - self.ambient_temp
        self.ambient_temp += clamp(diff * 0.05, -0.2, 0.2)
        self.ambient_temp += random.uniform(-0.05, 0.05)
        self.ambient_temp = clamp(self.ambient_temp, 5.0, 60.0)

        # Fan speed increases when temperature difference is larger
        self.fan_speed = clamp(5.0 + abs(diff) * 2.0 + random.uniform(-0.3, 0.3), 0.0, 40.0)

        # Outdoor values drift slowly
        self.outdoor_temp += random.uniform(-0.03, 0.03)
        self.outdoor_press += random.uniform(-0.2, 0.2)

        # Light intensity random walk
        self.light_intensity += random.randint(-2, 2)
        self.light_intensity = int(clamp(self.light_intensity, 0, 100))

        # Auto-close if it's dark
        if self.light_intensity < 25:
            self.desired_curtain = 100

        # Curtain position moves gradually toward desired
        if self.desired_curtain != self.current_curtain:
            step = 1 if self.desired_curtain > self.current_curtain else -1
            moves = max(1, int(dt * 10))
            for _ in range(moves):
                if self.desired_curtain == self.current_curtain:
                    break
                self.current_curtain += step
                self.current_curtain = int(clamp(self.current_curtain, 0, 100))

        self.last_error = ""


class AirConditionerSystemConnectionMock:
    # Mock API for Board #1

    def __init__(self, conn: HomeAutomationSystemConnectionMock):
        self.conn = conn

    def getDesiredTemp(self) -> float:
        return float(self.conn.desired_temp)

    def setDesiredTemp(self, value: float) -> None:
        self.conn.desired_temp = float(clamp(value, 10.0, 50.0))

    def getAmbientTemp(self) -> float:
        return float(self.conn.ambient_temp)

    def getFanSpeed(self) -> float:
        return float(self.conn.fan_speed)


class CurtainControlSystemConnectionMock:
    # Mock API for Board #2

    def __init__(self, conn: HomeAutomationSystemConnectionMock):
        self.conn = conn

    def getDesiredCurtain(self) -> int:
        return int(self.conn.desired_curtain)

    def setDesiredCurtain(self, value: int) -> None:
        self.conn.desired_curtain = int(clamp(value, 0, 100))

    def getCurrentCurtain(self) -> int:
        return int(self.conn.current_curtain)

    def getOutdoorTemp(self) -> float:
        return float(self.conn.outdoor_temp)

    def getOutdoorPress(self) -> float:
        return float(self.conn.outdoor_press)

    def getLightIntensity(self) -> int:
        return int(self.conn.light_intensity)


def build_mock_system(cfg: Dict) -> Dict:
    conn = HomeAutomationSystemConnectionMock(cfg["port_board1"], cfg["port_board2"], int(cfg["baudrate"]))
    aircon = AirConditionerSystemConnectionMock(conn)
    curtain = CurtainControlSystemConnectionMock(conn)
    return {"conn": conn, "aircon": aircon, "curtain": curtain}
