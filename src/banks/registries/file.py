# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
from pathlib import Path

from banks.registry import PromptTemplate, PromptTemplateIndex, TemplateNotFoundError


class FileTemplateRegistry:
    def __init__(self, user_data_path: Path) -> None:
        self._index_fpath: Path = user_data_path / "index.json"
        self._index: PromptTemplateIndex = PromptTemplateIndex(templates=[])
        try:
            self._index = PromptTemplateIndex.model_validate_json(self._index_fpath.read_text())
        except FileNotFoundError:
            # init the user data folder
            user_data_path.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _make_id(name: str, version: str | None):
        if version:
            return f"{name}:{version}"
        return name

    def save(self) -> None:
        with open(self._index_fpath, "w") as f:
            f.write(self._index.model_dump_json())

    def get(self, name: str, version: str | None = None) -> "PromptTemplate":
        tpl_id = self._make_id(name, version)
        for tpl in self._index.templates:
            if tpl_id == tpl.id:
                return tpl

        msg = f"cannot find template '{tpl_id}'"
        raise TemplateNotFoundError(msg)

    def set(self, *, name: str, prompt: str, version: str | None = None, overwrite: bool = False):
        try:
            tpl = self.get(name, version)
            if overwrite:
                tpl.prompt = prompt
                return
        except TemplateNotFoundError:
            tpl_id = self._make_id(name, version)
            tpl = PromptTemplate(id=tpl_id, name=name, version=version or "", prompt=prompt)
            self._index.templates.append(tpl)
