# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
class MissingDependencyError(Exception):
    """Some optional dependencies are missing."""


class AsyncError(Exception):
    """An error related to asyncio support."""


class CanaryWordError(Exception):
    """The canary word has leaked."""


class PromptNotFoundError(Exception):
    """The prompt was now found in the registry."""


class InvalidPromptError(Exception):
    """The prompt is not valid."""


class LLMError(Exception):
    """The LLM had problems."""
