# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
from pathlib import Path

from jinja2 import Environment
from jinja2.environment import Template
from pydantic_core import from_json

from banks.registry import PromptTemplate, PromptTemplateIndex, TemplateNotFoundError


class FileTemplateRegistry:
    def __init__(self, env: Environment, user_data_path: Path) -> None:
        self._env: Environment = env
        self._index_fpath: Path = user_data_path / "index.json"
        self._index: PromptTemplateIndex = PromptTemplateIndex(templates=[])
        try:
            self._index = PromptTemplateIndex.model_validate_json(self._index_fpath.read_text())
        except FileNotFoundError:
            # init the user data folder
            if not self._index_fpath.parent.exists():
                self._index_fpath.parent.mkdir()

    def save(self) -> None:
        with open(self._index_fpath, "w") as f:
            f.write(self._index.model_dump_json())

    def get(self, name: str, version: int | None) -> "Template":
        version = version or 1
        for tpl in self._index.templates:
            if tpl.name == name and tpl.version == version:
                return self._env.get_template(tpl.id)
        raise TemplateNotFoundError()

    def set(self, name: str, prompt: str, version: int | None = None):
        if version is not None:
            for tpl in self._index.templates:
                if tpl.name == name and tpl.version == version:
                    return

        version = version or 1
        tpl_id = f"{name}:{version}"
        tpl = PromptTemplate(id=tpl_id, name=name, version=version, prompt=prompt)
        self._index.templates.append(tpl)
