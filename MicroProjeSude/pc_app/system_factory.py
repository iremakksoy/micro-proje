from mock_api import build_mock_system
from real_uart_system import build_real_system


def build_system(cfg: dict) -> dict:
    # default: mock (safer)
    use_mock = cfg.get("use_mock", True)
    return build_mock_system(cfg) if use_mock else build_real_system(cfg)
