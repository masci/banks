# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
from jinja2 import Environment, PackageLoader

from .filters import lemmatize
from .extensions import GenerateExtension

# Init the Jinja env
env = Environment(loader=PackageLoader("banks", "templates"), extensions=[GenerateExtension])

# Setup custom filters
env.filters["lemmatize"] = lemmatize


def with_env(cls):
    """
    A decorator that adds an `env` attribute to the decorated class
    """

    class KlassWithEnv(cls):
        env = env

    return KlassWithEnv
