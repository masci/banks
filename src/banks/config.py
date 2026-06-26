# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
import os
import types as _types
import typing
from pathlib import Path
from typing import Any

from platformdirs import user_data_path

from .utils import strtobool


def _unwrap_optional(t: Any) -> Any:
    """Return the inner type of Optional[X] / X | None, or t unchanged."""
    origin = getattr(t, "__origin__", None)
    if origin is typing.Union:
        args = [a for a in t.__args__ if a is not None.__class__]
        if len(args) == 1:
            return args[0]
    if isinstance(t, _types.UnionType):
        args = [a for a in t.__args__ if a is not None.__class__]
        if len(args) == 1:
            return args[0]
    return t


class _BanksConfig:
    ASYNC_ENABLED: bool = False
    USER_DATA_PATH: Path = user_data_path("banks")
    MEDIA_ROOT: Path | None = None

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
        annotations = getattr(type(self), "__annotations__", {})
        t = _unwrap_optional(annotations.get(name, type(original_value)))
        if t is bool:
            return strtobool(read_value)
        if t is Any:
            return read_value

        return t(read_value)


config = _BanksConfig()
