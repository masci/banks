# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
from .config import config
from .env import env
from .prompt import AsyncPrompt, Prompt

__all__ = (
    "env",
    "Prompt",
    "AsyncPrompt",
    "config",
)

# Constants
DEFAULT_VERSION = "0"
INDEX_NAME = "index.json"
META_PATH = "meta"
