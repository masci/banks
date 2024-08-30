# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
import json
from pathlib import Path

from pydantic import BaseModel, Field

from banks import Prompt
from banks.registry import TemplateNotFoundError

# Constants
default_version = "0"
default_index_name = "index.json"
default_meta_path = "meta"


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
        self._index_path = self._path / default_index_name
        if not self._index_path.exists() or force_reindex:
            self._scan()
        else:
            self._load()
        self._meta_path = self._path / default_meta_path

    def _load(self):
        self._index = PromptFileIndex.model_validate_json(self._index_path.read_text())

    def _scan(self):
        self._index: PromptFileIndex = PromptFileIndex()
        for path in self._path.glob("*.jinja*"):
            pf = PromptFile(name=path.stem, version="0", path=path)
            self._index.files.append(pf)
        self._index_path.write_text(self._index.model_dump_json())

    def get(self, *, name: str, version: str | None = None) -> "Prompt":
        version = version or default_version
        for pf in self._index.files:
            if pf.name == name and pf.version == version and pf.path.exists():
                return Prompt(pf.path.read_text())
        raise TemplateNotFoundError

    def set(self, *, name: str, prompt: Prompt, version: str | None = None, overwrite: bool = False):
        version = version or default_version
        for pf in self._index.files:
            if pf.name == name and pf.version == version and overwrite:
                pf.path.write_text(prompt.raw)
                return
        new_prompt_file = self._path / f"{name}.{version}.jinja"
        new_prompt_file.write_text(prompt.raw)
        pf = PromptFile(name=name, version=version, path=new_prompt_file)
        self._index.files.append(pf)

    def get_meta(self, *, name: str, version: str | None = None) -> dict:
        version = version or default_version
        meta_path = self._meta_path / f"{name}.{version}.json"
        if not meta_path.exists():
            msg = f"Meta directory or file for prompt {name}:{version}.jinja not found."
            raise FileNotFoundError(msg)
        return json.loads(open(meta_path).read())

    def set_meta(self, *, meta: dict, name: str, version: str | None = None, overwrite: bool = False):
        version = version or default_version
        if not self._meta_path.exists():
            self._meta_path.mkdir()
        if Path(self._path / f"{name}.{version}.jinja") not in [pf.path for pf in self._index.files]:
            msg = f"Prompt {name}.{version}.jinja not found in the index. Cannot set meta for a non-existing prompt."
            raise ValueError(msg)

        if Path(self._meta_path / f"{name}.{version}.json") in list(self._meta_path.glob("*.json")):
            if not overwrite:
                msg = f"Meta file for prompt {name}:{version} already exists. Use overwrite=True to overwrite."
                raise ValueError(msg)
        meta_path = self._meta_path / f"{name}.{version}.json"
        meta_path.write_text(json.dumps(meta))
