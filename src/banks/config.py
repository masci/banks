import os

from .utils import strtobool

async_enabled = strtobool(os.environ.get("BANKS_ASYNC_ENABLED", "false"))
