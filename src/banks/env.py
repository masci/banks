# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
from jinja2 import Environment

from banks.extensions import GenerateExtension
from banks.filters import lemmatize
from banks.loader import MultiLoader

# Init the Jinja env
env = Environment(loader=MultiLoader(), extensions=[GenerateExtension], autoescape=False)

# Setup custom filters
env.filters["lemmatize"] = lemmatize


def with_env(cls):
    """
    A decorator that adds an `env` attribute to the decorated class
    """
    cls.env = env
    return cls
