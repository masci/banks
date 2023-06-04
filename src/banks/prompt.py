# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
from typing import Optional

from .env import with_env


@with_env
class Prompt:
    def __init__(self, text: Optional[str] = None) -> None:
        self._template = self.env.from_string(text) if text else None

    @classmethod
    def from_template(cls, name: str) -> 'Prompt':
        p = cls()
        p._template = cls.env.get_template(name)
        return p

    def text(self, data: Optional[dict] = None) -> str:
        data = data or {}
        return self._template.render(data)
