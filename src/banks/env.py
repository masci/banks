# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
import os

from jinja2 import Environment, select_autoescape

from banks.extensions import GenerateExtension, HFInferenceEndpointsExtension
from banks.filters import lemmatize
from banks.loader import MultiLoader


def strtobool(val: str) -> bool:
    """Convert a string representation of truth to True or False.

    True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
    are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
    'val' is anything else.
    """
    val = val.lower()
    if val in ("y", "yes", "t", "true", "on", "1"):
        return True
    elif val in ("n", "no", "f", "false", "off", "0"):
        return False
    else:
        msg = f"invalid truth value {val}"
        raise ValueError(msg)


async_enabled = strtobool(os.environ.get("BANKS_ASYNC_ENABLED", "false"))

# Init the Jinja env
env = Environment(
    loader=MultiLoader(),
    extensions=[GenerateExtension, HFInferenceEndpointsExtension],
    autoescape=select_autoescape(
        enabled_extensions=("html", "xml"),
        default_for_string=False,
    ),
    trim_blocks=True,
    lstrip_blocks=True,
    enable_async=bool(async_enabled),
)

# Setup custom filters
env.filters["lemmatize"] = lemmatize


def with_env(cls):
    """
    A decorator that adds an `env` attribute to the decorated class
    """
    cls.env = env
    return cls
