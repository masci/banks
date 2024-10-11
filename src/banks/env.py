# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
from jinja2 import Environment, PackageLoader, select_autoescape

from .config import config
from .filters import cache_control, lemmatize


def _add_extensions(_env):
    """
    We lazily add extensions so that we can use the env in the extensions themselves if needed.

    For example, we use banks to manage the system prompt in `GenerateExtension`
    """
    from .extensions.chat import ChatExtension  # pylint: disable=import-outside-toplevel
    from .extensions.completion import CompletionExtension  # pylint: disable=import-outside-toplevel
    from .extensions.generate import GenerateExtension  # pylint: disable=import-outside-toplevel
    from .extensions.inference_endpoint import HFInferenceEndpointsExtension  # pylint: disable=import-outside-toplevel

    _env.add_extension(ChatExtension)
    _env.add_extension(CompletionExtension)
    _env.add_extension(GenerateExtension)
    _env.add_extension(HFInferenceEndpointsExtension)


# Init the Jinja env
env = Environment(
    loader=PackageLoader("banks", "internal"),
    autoescape=select_autoescape(
        enabled_extensions=("html", "xml"),
        default_for_string=False,
    ),
    trim_blocks=True,
    lstrip_blocks=True,
    enable_async=bool(config.ASYNC_ENABLED),
)


# Setup custom filters and defaults
env.filters["lemmatize"] = lemmatize
env.filters["cache_control"] = cache_control
_add_extensions(env)
