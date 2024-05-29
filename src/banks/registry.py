# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
from dataclasses import dataclass
from typing import Protocol
from jinja2.environment import Template


@dataclass
class PromptTemplate:
    id: str
    name: str
    version: int
    prompt: str


class TemplateRegistry(Protocol):
    def save(self) -> None: ...

    def get(self, name: str, version: int | None) -> "Template": ...

    def set(self, name: str, version: int | None): ...
