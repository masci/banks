# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
from typing import Optional

from .config import async_enabled
from .env import env
from .errors import AsyncError
from .utils import generate_canary_word


class BasePrompt:
    def __init__(self, text: str, canary_word: Optional[str] = None) -> None:
        self._template = env.from_string(text)
        self.defaults = {"canary_word": canary_word or generate_canary_word()}

    def _get_context(self, data: Optional[dict]) -> dict:
        if data is None:
            return self.defaults
        return data | self.defaults

    def canary_leaked(self, text: str) -> bool:
        return self.defaults["canary_word"] in text

    @classmethod
    def from_template(cls, name: str) -> "BasePrompt":
        p = cls("")
        p._template = env.get_template(name)
        return p


class Prompt(BasePrompt):
    def text(self, data: Optional[dict] = None) -> str:
        data = self._get_context(data)
        return self._template.render(data)


class AsyncPrompt(BasePrompt):
    def __init__(self, text: str) -> None:
        super().__init__(text)

        if not async_enabled:
            msg = "Async is not enabled. Please set the environment variable 'BANKS_ASYNC_ENABLED=on' and try again."
            raise AsyncError(msg)

    async def text(self, data: Optional[dict] = None) -> str:
        data = self._get_context(data)
        result: str = await self._template.render_async(data)
        return result
