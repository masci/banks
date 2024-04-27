# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
from typing import Optional

from banks.env import async_enabled, env
from banks.errors import AsyncError


class BasePrompt:
    def __init__(self, text: str) -> None:
        self._template = env.from_string(text)

    @classmethod
    def from_template(cls, name: str) -> "BasePrompt":
        p = cls("")
        p._template = env.get_template(name)
        return p


class Prompt(BasePrompt):
    def text(self, data: Optional[dict] = None) -> str:
        data = data or {}
        return self._template.render(data)


class AsyncPrompt(BasePrompt):
    def __init__(self, text: str) -> None:
        super().__init__(text)

        if not async_enabled:
            msg = "Async is not enabled. Please set the environment variable 'BANKS_ASYNC_ENABLED=on' and try again."
            raise AsyncError(msg)

    async def text(self, data: Optional[dict] = None) -> str:
        data = data or {}
        result: str = await self._template.render_async(data)
        return result
