# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
from typing import Callable

from banks.types import Tool


def tool(value: Callable) -> str:
    tool = Tool.from_callable(value)
    return tool.model_dump_json()
