# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
from jinja2 import Environment, select_autoescape

from .config import config
from .filters import lemmatize
from .loader import MultiLoader


def _add_extensions(env):
    """
    We lazily add extensions so that we can use the env in the extensions themselves if needed.

    For example, we use banks to manage the system prompt in `GenerateExtension`
    """
    from .extensions import GenerateExtension, HFInferenceEndpointsExtension

    env.add_extension(GenerateExtension)
    env.add_extension(HFInferenceEndpointsExtension)


# Init the Jinja env
env = Environment(
    loader=MultiLoader(),
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
_add_extensions(env)
