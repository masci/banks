# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
from jinja2 import Environment, select_autoescape

from .config import config
from .filters import audio, cache_control, image, lemmatize, tool


def _add_extensions(_env):
    """
    We lazily add extensions so that we can use the env in the extensions themselves if needed.

    For example, we use banks to manage the system prompt in `GenerateExtension`
    """
    from .extensions.chat import ChatExtension  # pylint: disable=import-outside-toplevel
    from .extensions.completion import CompletionExtension  # pylint: disable=import-outside-toplevel

    _env.add_extension(ChatExtension)
    _env.add_extension(CompletionExtension)


# Init the Jinja env
env = Environment(
    autoescape=select_autoescape(
        enabled_extensions=("html", "xml"),
        default_for_string=False,
    ),
    trim_blocks=True,
    lstrip_blocks=True,
    enable_async=bool(config.ASYNC_ENABLED),
)


# Setup custom filters and defaults
env.filters["cache_control"] = cache_control
env.filters["image"] = image
env.filters["lemmatize"] = lemmatize
env.filters["tool"] = tool
env.filters["audio"] = audio

_add_extensions(env)
