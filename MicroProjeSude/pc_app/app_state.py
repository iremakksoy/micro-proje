import json
import os
from typing import Any, Dict

DEFAULT_CONFIG: Dict[str, Any] = {
    "port_board1": "COM3",
    "port_board2": "COM4",
    "baudrate": 9600,
    "refresh_interval_ms": 500,
    "use_mock": True,
}


def load_config(path: str = "config.json") -> Dict[str, Any]:
    # Load config from JSON; if missing or broken, fall back to defaults.
    data: Dict[str, Any] = {}
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f) or {}
        except Exception:
            data = {}

    cfg = DEFAULT_CONFIG.copy()
    cfg.update(data)

    if not os.path.exists(path):
        save_config(cfg, path)

    return cfg


def save_config(cfg: Dict[str, Any], path: str = "config.json") -> None:
    # Save config to JSON.
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)
