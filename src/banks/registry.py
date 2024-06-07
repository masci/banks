# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
from typing import Protocol

from pydantic import BaseModel


class TemplateNotFoundError(Exception): ...


class InvalidTemplateError(Exception): ...


class PromptTemplate(BaseModel):
    id: str
    name: str
    version: str
    prompt: str


class PromptTemplateIndex(BaseModel):
    templates: list[PromptTemplate]


class TemplateRegistry(Protocol):
    def get(self, *, name: str, version: str | None = None) -> "PromptTemplate": ...

    def set(self, *, name: str, prompt: str, version: str | None = None, overwrite: bool = False): ...
