# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
from pathlib import Path

from pydantic import BaseModel, Field

from banks import Prompt
from banks.registry import TemplateNotFoundError


class PromptFile(BaseModel):
    name: str
    version: str
    path: Path


class PromptFileIndex(BaseModel):
    files: list[PromptFile] = Field(default=[])


class DirectoryTemplateRegistry:
    def __init__(self, directory_path: Path, *, force_reindex: bool = False):
        if not directory_path.is_dir():
            msg = "{directory_path} must be a directory."
            raise ValueError(msg)

        self._path = directory_path
        self._index_path = self._path / "index.json"
        if not self._index_path.exists() or force_reindex:
            self._scan()
        else:
            self._load()

    def _load(self):
        self._index = PromptFileIndex.model_validate_json(self._index_path.read_text())

    def _scan(self):
        self._index: PromptFileIndex = PromptFileIndex()
        for path in self._path.glob("*.jinja*"):
            pf = PromptFile(name=path.stem, version="0", path=path)
            self._index.files.append(pf)
        self._index_path.write_text(self._index.model_dump_json())

    def get(self, *, name: str, version: str | None = None) -> "Prompt":
        version = version or "0"
        for pf in self._index.files:
            if pf.name == name and pf.version == version and pf.path.exists():
                return Prompt(pf.path.read_text())
        raise TemplateNotFoundError

    def set(self, *, name: str, prompt: Prompt, version: str | None = None, overwrite: bool = False):
        version = version or "0"
        for pf in self._index.files:
            if pf.name == name and pf.version == version and overwrite:
                pf.path.write_text(prompt.raw)
                return
        new_prompt_file = self._path / "{name}.{version}.jinja"
        new_prompt_file.write_text(prompt.raw)
        pf = PromptFile(name=name, version=version, path=new_prompt_file)
        self._index.files.append(pf)
