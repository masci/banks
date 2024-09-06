# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
from typing import Protocol

from .prompt import Prompt


class TemplateNotFoundError(Exception): ...


class InvalidTemplateError(Exception): ...


class TemplateRegistry(Protocol):
    def get(self, *, name: str, version: str | None = None) -> "Prompt": ...

    def set(self, *, name: str, prompt: Prompt, version: str | None = None, overwrite: bool = False): ...
