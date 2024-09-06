# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
import time
from pathlib import Path

from pydantic import BaseModel, Field

from banks import Prompt
from banks.registry import TemplateNotFoundError

# Constants
DEFAULT_VERSION = "0"
DEFAULT_INDEX_NAME = "index.json"


class PromptFile(BaseModel):
    name: str
    version: str
    path: Path
    meta: dict


class PromptFileIndex(BaseModel):
    files: list[PromptFile] = Field(default=[])


class DirectoryTemplateRegistry:
    def __init__(self, directory_path: Path, *, force_reindex: bool = False):
        if not directory_path.is_dir():
            msg = "{directory_path} must be a directory."
            raise ValueError(msg)

        self._path = directory_path
        self._index_path = self._path / DEFAULT_INDEX_NAME
        if not self._index_path.exists() or force_reindex:
            self._scan()
        else:
            self._load()

    def _load(self):
        self._index = PromptFileIndex.model_validate_json(self._index_path.read_text())

    def _scan(self):
        self._index: PromptFileIndex = PromptFileIndex()
        for path in self._path.glob("*.jinja*"):
            name, version = path.stem.rsplit(".", 1) if "." in path.stem else (path.stem, DEFAULT_VERSION)
            pf = PromptFile(name=name, version=version, path=path, meta={})
            self._index.files.append(pf)
        self._index_path.write_text(self._index.model_dump_json())

    def get(self, *, name: str, version: str = DEFAULT_VERSION) -> "PromptFile":
        for pf in self._index.files:
            if pf.name == name and pf.version == version and pf.path.exists():
                return pf
        raise TemplateNotFoundError

    def get_prompt(self, *, name: str, version: str = DEFAULT_VERSION) -> Prompt:
        return Prompt(self.get(name=name, version=version).path.read_text())

    def _get_prompt_file(self, *, name: str, version: str) -> PromptFile | None:
        for pf in self._index.files:
            if pf.name == name and pf.version == version:
                return pf
        return None

    def _create_pf(self, *, name: str, prompt: Prompt, version: str, overwrite: bool, meta: dict) -> "PromptFile":
        pf = self._get_prompt_file(name=name, version=version)
        if pf:
            if not overwrite:
                msg = f"Prompt {name}.{version}.jinja already exists. Use overwrite=True to overwrite."
                raise ValueError(msg)
            pf.path.write_text(prompt.raw)
            pf.meta = meta
            return pf
        new_prompt_file = self._path / f"{name}.{version}.jinja"
        new_prompt_file.write_text(prompt.raw)
        pf = PromptFile(name=name, version=version, path=new_prompt_file, meta=meta)
        return pf

    def set(
        self,
        *,
        name: str,
        prompt: Prompt,
        meta: dict | None = None,
        version: str = DEFAULT_VERSION,
        overwrite: bool = False,
    ):
        meta = {**(meta or {}), "created_at": time.ctime()}

        pf = self._create_pf(name=name, prompt=prompt, version=version, overwrite=overwrite, meta=meta)
        if pf not in self._index.files:
            self._index.files.append(pf)
        self._index_path.write_text(self._index.model_dump_json())

    def get_meta(self, *, name: str, version: str = DEFAULT_VERSION) -> dict:
        return self.get(name=name, version=version).meta

    def update_meta(self, *, meta: dict, name: str, version: str = DEFAULT_VERSION):
        pf = self._get_prompt_file(name=name, version=version)
        if not pf:
            unk_err = f"Prompt {name}.{version} not found in the index. Cannot set meta for a non-existing prompt."
            raise ValueError(unk_err)
        pf.meta = meta
        self._index_path.write_text(self._index.model_dump_json())
