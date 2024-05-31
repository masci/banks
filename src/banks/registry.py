# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
from typing import Protocol

from jinja2.environment import Template
from pydantic import BaseModel


class TemplateNotFoundError(Exception): ...


class PromptTemplate(BaseModel):
    id: str
    name: str
    version: int
    prompt: str


class PromptTemplateIndex(BaseModel):
    templates: list[PromptTemplate]


class TemplateRegistry(Protocol):
    def save(self) -> None: ...

    def get(self, name: str, version: int | None) -> "Template": ...

    def set(self, name: str, prompt: str, version: int | None = None): ...
