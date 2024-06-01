import os

from platformdirs import user_data_path

from .utils import strtobool


class BanksConfig:
    ASYNC_ENABLED = strtobool(os.environ.get("BANKS_ASYNC_ENABLED", "false"))
    USER_DATA_PATH = user_data_path(os.environ.get("BANKS_USER_DATA_PATH", "banks"))


config = BanksConfig()
