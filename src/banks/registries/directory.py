# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
import json
import os
import time
from pathlib import Path

from pydantic import BaseModel, Field

from banks import Prompt
from banks.registry import TemplateNotFoundError

# Constants
DEFAULT_VERSION = "0"
DEFAULT_INDEX_NAME = "index.json"
DEFAULT_META_PATH = "meta"


class PromptFile(BaseModel):
    name: str
    version: str
    path: Path
    meta_path: Path


class PromptFileIndex(BaseModel):
    files: list[PromptFile] = Field(default=[])


class DirectoryTemplateRegistry:
    def __init__(self, directory_path: Path, *, force_reindex: bool = False):
        if not directory_path.is_dir():
            msg = "{directory_path} must be a directory."
            raise ValueError(msg)

        self._path = directory_path
        os.makedirs(self._path / DEFAULT_META_PATH, exist_ok=True)
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
            meta_file = self._path / DEFAULT_META_PATH / f"{path.stem}.json"
            pf = PromptFile(name=path.stem, version="0", path=path, meta_path=meta_file)
            self._index.files.append(pf)
        self._index_path.write_text(self._index.model_dump_json())

    def get(self, *, name: str, version: str | None = None) -> "Prompt":
        version = version or DEFAULT_VERSION
        for pf in self._index.files:
            if pf.name == name and pf.version == version and pf.path.exists():
                return Prompt(pf.path.read_text())
        raise TemplateNotFoundError

    def _create_new_prompt_and_meta(self, *, name: str, prompt: Prompt, meta: dict, version: str | None = None):
        new_prompt_file = self._path / f"{name}.{version}.jinja"
        new_prompt_file.write_text(prompt.raw)
        new_meta_file = self._path / DEFAULT_META_PATH / f"{name}.{version}.json"
        new_meta_file.write_text(json.dumps({**meta, "created_at": time.ctime()}))
        return new_prompt_file, new_meta_file

    def _set_prompt_and_meta(  # pylint: disable=too-many-arguments
        self, *, name: str, prompt: Prompt, meta: dict, version: str | None = None, overwrite: bool = False
    ):
        for pf in self._index.files:
            if pf.name == name and pf.version == version:
                if not overwrite:
                    msg = f"Prompt {name}.{version}.jinja already exists. Use overwrite=True to overwrite."
                    raise ValueError(msg)
                pf.path.write_text(prompt.raw)
                current_meta = json.loads(pf.meta_path.read_text())
                pf.meta_path.write_text(json.dumps({**current_meta, **meta}))
                return pf.path, pf.meta_path
        return self._create_new_prompt_and_meta(name=name, prompt=prompt, meta=meta, version=version)

    def set(  # pylint: disable=too-many-arguments
        self,
        *,
        name: str,
        prompt: Prompt,
        meta: dict | None = None,
        version: str | None = None,
        overwrite: bool = False,
    ):
        version = version or DEFAULT_VERSION
        meta = {**(meta or {}), "created_at": time.ctime()}

        prompt_file, meta_file = self._set_prompt_and_meta(
            name=name, prompt=prompt, meta=meta, version=version, overwrite=overwrite
        )
        pf = PromptFile(name=name, version=version, path=prompt_file, meta_path=meta_file)
        if pf not in self._index.files:
            self._index.files.append(pf)

    def get_meta(self, *, name: str, version: str | None = None) -> dict:
        version = version or DEFAULT_VERSION
        for pf in self._index.files:
            if pf.name == name and pf.version == version and pf.meta_path.exists():
                return json.loads(open(pf.meta_path, encoding="utf-8").read())
        return {}

    def update_meta(self, *, meta: dict, name: str, version: str | None = None):
        version = version or DEFAULT_VERSION
        for pf in self._index.files:
            if pf.name == name and pf.version == version and pf.meta_path.exists():
                current_meta = self.get_meta(name=name, version=version)
                pf.meta_path.write_text(json.dumps({**current_meta, **meta}))
                return pf.meta_path
        unk_err = f"Unknown prompt {name}.{version}.jinja, Cannot set meta for a non-existing prompt."
        raise ValueError(unk_err)
