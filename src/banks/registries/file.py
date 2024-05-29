# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
from pathlib import Path
import json

from jinja2.environment import Template

from banks.env import env, USER_DATA_PATH
from banks.registry import PromptTemplate


class FileTemplateRegistry:
    def __init__(self) -> None:
        self._index_fpath = USER_DATA_PATH / "index.json"
        self._index: list[PromptTemplate] = json.loads(self._index_fpath.read_text())

    def save(self) -> None:
        with open(self._index_fpath, "w") as f:
            json.dump(self._index, f)

    def get(self, name: str, version: int | None) -> "Template":
        version = version or 1
        for tpl in self._index:
            if tpl.name == name and tpl.version == version:
                return env.get_template(tpl.id)
        raise ValueError("Not found")

    def set(self, name: str, prompt: str, version: int | None):
        if version is not None:
            for tpl in self._index:
                if tpl.name == name and tpl.version == version:
                    return

        version = version or 1
        tpl_id = f"{name}:{version}"
        tpl = PromptTemplate(tpl_id, name, version, prompt)
        self._index.append(tpl)
