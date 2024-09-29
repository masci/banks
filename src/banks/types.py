# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
from typing import Any, Protocol, Self

from pydantic import BaseModel

from .prompt import Prompt


class PromptRegistry(Protocol):  # pragma: no cover
    """Interface to be implemented by concrete prompt registries."""

    def get(self, *, name: str, version: str | None = None) -> Prompt: ...

    def set(self, *, prompt: Prompt, overwrite: bool = False) -> None: ...


class PromptModel(BaseModel):
    """Serializable representation of a Prompt."""

    text: str
    name: str | None = None
    version: str | None = None
    metadata: dict[str, Any] | None = None

    @classmethod
    def from_prompt(cls: type[Self], prompt: Prompt) -> Self:
        return cls(text=prompt.raw, name=prompt.name, version=prompt.version, metadata=prompt.metadata)
