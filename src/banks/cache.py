# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
import pickle
from typing import Optional, Protocol, runtime_checkable


@runtime_checkable
class RenderCache(Protocol):  # pragma: no cover
    """
    Interface for rendering cache.

    Prompts with the same template and same context are retrieved from the cache directly,
    instead of going through the rendering process.
    """

    def get(self, context: dict) -> Optional[str]: ...

    def set(self, context: dict, prompt: str) -> None: ...

    def clear(self) -> None: ...


class DefaultCache:
    """
    In-memory, default rendering cache.
    """

    def __init__(self) -> None:
        self._cache: dict[bytes, str] = {}

    def get(self, context: dict) -> Optional[str]:
        return self._cache.get(pickle.dumps(context, pickle.HIGHEST_PROTOCOL))

    def set(self, context: dict, prompt: str) -> None:
        self._cache[pickle.dumps(context, pickle.HIGHEST_PROTOCOL)] = prompt

    def clear(self) -> None:
        self._cache = {}
