# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
"""
Directory-based prompt registry implementation that stores prompts as files.
"""

from __future__ import annotations

import os
import time
from pathlib import Path

try:
    from typing import Self
except ImportError:  # pragma: no cover
    from typing_extensions import Self
from pydantic import BaseModel, Field

from banks import Prompt
from banks.errors import InvalidPromptError, PromptNotFoundError
from banks.prompt import DEFAULT_VERSION, PromptModel

# Constants
DEFAULT_INDEX_NAME = "index.json"


def _write_file_no_follow(path: Path, content: str) -> None:
    """Write content to a file, strictly refusing to follow symbolic links."""
    no_follow = getattr(os, "O_NOFOLLOW", None)
    if no_follow is not None:
        try:
            fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_TRUNC | no_follow)
        except OSError as exc:
            msg = f"Path is a symbolic link or cannot be opened: {path}"
            raise InvalidPromptError(msg) from exc
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
    else:
        # Platform does not support O_NOFOLLOW (e.g. Windows);
        # rely on earlier symlink checks in _resolve_prompt_file and _validate_index_path.
        path.write_text(content, encoding="utf-8")


def _resolve_prompt_file(registry_root: Path, name: str, version: str) -> Path:
    """Resolve the on-disk path for a prompt file, ensuring it stays within ``registry_root``."""
    if Path(name).is_absolute():
        msg = f"Invalid prompt name: {name!r}"
        raise InvalidPromptError(msg)
    if Path(version).is_absolute():
        msg = f"Invalid prompt version: {version!r}"
        raise InvalidPromptError(msg)
    if "/" in version or "\\" in version or version in (".", ".."):
        msg = f"Invalid prompt version: {version!r}"
        raise InvalidPromptError(msg)
    for part in Path(name).parts:
        if part in (".", ".."):
            msg = f"Invalid prompt name: {name!r}"
            raise InvalidPromptError(msg)

    root = registry_root.resolve()
    candidate = registry_root / f"{name}.{version}.jinja"
    if candidate.is_symlink():
        msg = f"Prompt path is a symbolic link: {candidate}"
        raise InvalidPromptError(msg)
    resolved = candidate.resolve()
    if not resolved.is_relative_to(root):
        msg = f"Prompt path escapes registry root: {resolved}"
        raise InvalidPromptError(msg)
    if version == DEFAULT_VERSION and not resolved.exists():
        alt_raw = registry_root / f"{name}.jinja"
        if alt_raw.is_symlink():
            msg = f"Prompt path is a symbolic link: {alt_raw}"
            raise InvalidPromptError(msg)
        alt = alt_raw.resolve()
        if alt.exists() and alt.is_relative_to(root):
            return alt_raw
    return candidate


class PromptFile(PromptModel):
    """Model representing a prompt file stored on disk."""

    path: Path | None = Field(default=None, exclude=True)

    @classmethod
    def from_prompt_path(cls: type[Self], prompt: Prompt, path: Path) -> Self:
        """
        Create a PromptFile instance from a Prompt object and save it to disk.

        Args:
            prompt: The Prompt object to save
            path: Directory path where the prompt file should be stored

        Returns:
            A new PromptFile instance
        """
        version = prompt.version or DEFAULT_VERSION
        prompt_file = _resolve_prompt_file(path, prompt.name, version)
        prompt_file.parent.mkdir(parents=True, exist_ok=True)
        _write_file_no_follow(prompt_file, prompt.raw)
        return cls(
            text=prompt.raw, name=prompt.name, version=prompt.version, metadata=prompt.metadata, path=prompt_file
        )


class PromptFileIndex(BaseModel):
    """Index tracking all prompt files in the directory."""

    files: list[PromptFile] = Field(default=[])


class DirectoryPromptRegistry:
    """Registry that stores prompts as files in a directory structure."""

    def __init__(self, directory_path: str | Path, *, force_reindex: bool = False):
        """
        Initialize the directory prompt registry.

        Args:
            directory_path: Path to directory where prompts will be stored
            force_reindex: Whether to force rebuilding the index from disk

        Raises:
            ValueError: If directory_path is not a directory
        """
        dir_path = Path(directory_path)
        if not dir_path.is_dir():
            msg = f"{directory_path} must be a directory."
            raise ValueError(msg)

        self._path = dir_path
        self._index_path = self._path / DEFAULT_INDEX_NAME
        if not self._index_path.exists() or force_reindex:
            self._scan()
        else:
            self._load()

    def _validate_index_path(self):
        if self._index_path.is_symlink():
            msg = f"Index file cannot be a symbolic link: {self._index_path}"
            raise InvalidPromptError(msg)
        if self._index_path.exists() and not self._index_path.resolve().is_relative_to(self._path.resolve()):
            msg = f"Index file escapes registry root: {self._index_path}"
            raise InvalidPromptError(msg)

    @property
    def path(self) -> Path:
        """Get the directory path where prompts are stored."""
        return self._path

    def get(self, *, name: str, version: str | None = None) -> Prompt:
        """
        Retrieve a prompt by name and version.

        Args:
            name: Name of the prompt to retrieve
            version: Version of the prompt (optional)

        Returns:
            The requested Prompt object

        Raises:
            PromptNotFoundError: If prompt doesn't exist
        """
        version = version or DEFAULT_VERSION
        for pf in self._index.files:
            if pf.name == name and pf.version == version and pf.path and pf.path.exists():
                return Prompt(**pf.model_dump())
        raise PromptNotFoundError

    def set(self, *, prompt: Prompt, overwrite: bool = False):
        """
        Store a prompt in the registry.

        Args:
            prompt: The Prompt object to store
            overwrite: Whether to overwrite existing prompt

        Raises:
            InvalidPromptError: If prompt exists and overwrite=False
        """
        try:
            version = prompt.version or DEFAULT_VERSION
            idx, pf = self._get_prompt_file(name=prompt.name, version=version)
            if overwrite:
                prompt.metadata["created_at"] = time.ctime()
                self._index.files[idx] = PromptFile.from_prompt_path(prompt, self._path)
                self._save()
            else:  # pylint: disable=duplicate-code
                msg = f"Prompt with name '{prompt.name}' already exists. Use overwrite=True to overwrite"
                raise InvalidPromptError(msg)
        except PromptNotFoundError:
            prompt.metadata["created_at"] = time.ctime()
            pf = PromptFile.from_prompt_path(prompt, self._path)
            self._index.files.append(pf)
            self._save()

    def _load(self):
        """Load the prompt index from disk."""
        self._validate_index_path()
        self._index = PromptFileIndex.model_validate_json(self._index_path.read_text(encoding="utf-8"))
        # Reconstruct the file paths since they're excluded from serialization
        for pf in self._index.files:
            version = pf.version or DEFAULT_VERSION
            pf.path = _resolve_prompt_file(self._path, pf.name, version)

    def _save(self):
        """Save the prompt index to disk."""
        self._validate_index_path()
        _write_file_no_follow(self._index_path, self._index.model_dump_json())

    def _scan(self):
        """Scan directory for prompt files and build the index."""
        self._validate_index_path()
        self._index = PromptFileIndex()
        root = self._path.resolve()
        for path in sorted(self._path.rglob("*.jinja")):
            if not path.is_file():
                continue
            if path.is_symlink():
                msg = f"Symbolic links are not allowed in prompt registry: {path}"
                raise InvalidPromptError(msg)
            resolved = path.resolve()
            if not resolved.is_relative_to(root):
                msg = f"Prompt path escapes registry root: {path}"
                raise InvalidPromptError(msg)

            rel = path.relative_to(self._path)
            stem = rel.stem
            name_part, version = stem.rsplit(".", 1) if "." in stem else (stem, DEFAULT_VERSION)
            full_name = f"{rel.parent.as_posix()}/{name_part}" if str(rel.parent) != "." else name_part

            with path.open("r", encoding="utf-8") as f:
                pf = PromptFile(text=f.read(), name=full_name, version=version, path=path, metadata={})
                self._index.files.append(pf)
        self._save()

    def _get_prompt_file(self, *, name: str | None, version: str) -> tuple[int, PromptFile]:
        """
        Find a prompt file in the index.

        Args:
            name: Name of the prompt
            version: Version of the prompt

        Returns:
            Tuple of (index position, PromptFile)

        Raises:
            PromptNotFoundError: If prompt doesn't exist in index
        """
        for i, pf in enumerate(self._index.files):
            if pf.name == name and pf.version == version:
                return i, pf

        msg = f"cannot find prompt with name '{name}' and version '{version}'"
        raise PromptNotFoundError(msg)
