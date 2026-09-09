# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
from __future__ import annotations

import sys

# Python < 3.11 does not have typing.NotRequired.
# Some third-party packages in our dependency tree import it from typing
# unconditionally. Patch it in early to prevent ImportError.
if sys.version_info < (3, 11):  # pylint: disable=wrong-import-position
    import typing

    import typing_extensions

    typing.NotRequired = typing_extensions.NotRequired

from .config import config
from .env import env
from .prompt import AsyncPrompt, Prompt
from .types import ChatMessage

__all__ = ("env", "Prompt", "AsyncPrompt", "config", "ChatMessage")
