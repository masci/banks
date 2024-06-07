# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
from typing import Protocol

from pydantic import BaseModel, Field


class TemplateNotFoundError(Exception): ...


class InvalidTemplateError(Exception): ...


class PromptTemplateMeta(BaseModel):
    key: str
    value: str | int | float


class PromptTemplate(BaseModel):
    id: str
    name: str
    prompt: str
    version: str = Field(default="")
    meta: list[PromptTemplateMeta] = Field(default=[])


class PromptTemplateIndex(BaseModel):
    templates: list[PromptTemplate]


class TemplateRegistry(Protocol):
    def get(self, *, name: str, version: str | None = None) -> "PromptTemplate": ...

    def set(self, *, name: str, prompt: str, version: str | None = None, overwrite: bool = False): ...
