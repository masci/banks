import os

from platformdirs import user_data_path

from .utils import strtobool

ASYNC_ENABLED = strtobool(os.environ.get("BANKS_ASYNC_ENABLED", "false"))
USER_DATA_PATH = user_data_path("banks")
