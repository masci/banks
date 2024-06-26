# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
from pathlib import Path

from pydantic import BaseModel

from banks.prompt import Prompt
from banks.registry import InvalidTemplateError, TemplateNotFoundError


class PromptTemplate(BaseModel):
    id: str | None
    name: str
    version: str
    prompt: str


class PromptTemplateIndex(BaseModel):
    templates: list[PromptTemplate]


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
        if ":" in name:
            msg = "Template name cannot contain ':'"
            raise InvalidTemplateError(msg)
        if version:
            return f"{name}:{version}"
        return name

    def save(self) -> None:
        with open(self._index_fpath, "w", encoding="locale") as f:
            f.write(self._index.model_dump_json())

    def get(self, name: str, version: str | None = None) -> "Prompt":
        tpl_id = self._make_id(name, version)
        tpl = self._get_template(tpl_id)
        return Prompt(tpl.prompt)

    def _get_template(self, tpl_id: str) -> "PromptTemplate":
        for tpl in self._index.templates:
            if tpl_id == tpl.id:
                return tpl

        msg = f"cannot find template '{id}'"
        raise TemplateNotFoundError(msg)

    def set(self, *, name: str, prompt: Prompt, version: str | None = None, overwrite: bool = False):
        tpl_id = self._make_id(name, version)
        try:
            tpl = self._get_template(tpl_id)
            if overwrite:
                tpl.prompt = prompt.raw
                self.save()
        except TemplateNotFoundError:
            tpl = PromptTemplate(id=tpl_id, name=name, version=version or "", prompt=prompt.raw)
            self._index.templates.append(tpl)
            self.save()
