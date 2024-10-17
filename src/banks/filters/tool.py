# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
from typing import Callable

from banks.types import Tool


def tool(function: Callable) -> str:
    """Inspect a Python callable and generates a JSON-schema ready for LLM function calling.

    Important:
        This filter only works when used within a `{% completion %}` block.
    """
    t = Tool.from_callable(function)
    return t.model_dump_json() + "\n"
