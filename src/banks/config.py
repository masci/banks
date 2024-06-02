import os
from pathlib import Path

from platformdirs import user_data_path

from .utils import strtobool


class BanksConfig:
    ASYNC_ENABLED: bool = strtobool(os.environ.get("BANKS_ASYNC_ENABLED", "false"))
    USER_DATA_PATH: Path = Path(os.environ.get("BANKS_USER_DATA_PATH", "")) or user_data_path("banks")


config = BanksConfig()
