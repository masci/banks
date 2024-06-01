# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
import os
from pathlib import Path

from jinja2 import Environment, select_autoescape


from .config import ASYNC_ENABLED, USER_DATA_PATH
from .filters import lemmatize
from .loader import MultiLoader
from .registries import FileTemplateRegistry
from .registry import TemplateRegistry


def _add_extensions(env):
    """
    We lazily add extensions so that we can use the env in the extensions themselves if needed.

    For example, we use banks to manage the system prompt in `GenerateExtension`
    """
    from .extensions import GenerateExtension, HFInferenceEndpointsExtension

    env.add_extension(GenerateExtension)
    env.add_extension(HFInferenceEndpointsExtension)


def _add_default_templates(r: TemplateRegistry):
    templates_dir = Path(os.path.dirname(__file__)) / "templates"
    for tpl_file in templates_dir.glob("*.jinja"):
        r.set(tpl_file.name, tpl_file.read_text())
    r.save()


# Init the Jinja env
env = Environment(
    loader=MultiLoader(),
    autoescape=select_autoescape(
        enabled_extensions=("html", "xml"),
        default_for_string=False,
    ),
    trim_blocks=True,
    lstrip_blocks=True,
    enable_async=bool(ASYNC_ENABLED),
)

# Init the Template registry
registry = FileTemplateRegistry(USER_DATA_PATH)


# Setup custom filters and defaults
env.filters["lemmatize"] = lemmatize
_add_extensions(env)
_add_default_templates(registry)
