# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
import os
from pathlib import Path
from typing import Any

from platformdirs import user_data_path

from .utils import strtobool


class _BanksConfig:
    ASYNC_ENABLED: bool = False
    USER_DATA_PATH: Path = user_data_path("banks")

    def __init__(self, env_var_prefix: str = "BANKS_"):
        self._env_var_prefix = env_var_prefix

    def __getattribute__(self, name: str) -> Any:
        # Raise an attribute error if the name of the config is unknown
        original_value = super().__getattribute__(name)

        # Env var takes precedence
        prefix = super().__getattribute__("_env_var_prefix")
        read_value = os.environ.get(f"{prefix}{name}")
        if read_value is None:
            return original_value

        # Convert string from env var to the actual type
        t = super().__getattribute__("__annotations__")[name]
        if t is bool:
            return strtobool(read_value)

        return t(read_value)


config = _BanksConfig()
