# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
from typing import Optional

from banks.env import env


class Prompt:
    def __init__(self, text: str) -> None:
        self._template = env.from_string(text)

    @classmethod
    def from_template(cls, name: str) -> "Prompt":
        p = cls("")
        p._template = env.get_template(name)
        return p

    def text(self, data: Optional[dict] = None) -> str:
        data = data or {}
        return self._template.render(data)
