# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
"""
Directory-based prompt registry implementation that stores prompts as files.
"""

from __future__ import annotations

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
        prompt_file = path / f"{prompt.name}.{prompt.version}.jinja"
        prompt_file.write_text(prompt.raw)
        return cls(
            text=prompt.raw, name=prompt.name, version=prompt.version, metadata=prompt.metadata, path=prompt_file
        )


class PromptFileIndex(BaseModel):
    """Index tracking all prompt files in the directory."""

    files: list[PromptFile] = Field(default=[])


class DirectoryPromptRegistry:
    """Registry that stores prompts as files in a directory structure."""

    def __init__(self, directory_path: str, *, force_reindex: bool = False):
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
            msg = "{directory_path} must be a directory."
            raise ValueError(msg)

        self._path = dir_path
        self._index_path = self._path / DEFAULT_INDEX_NAME
        if not self._index_path.exists() or force_reindex:
            self._scan()
        else:
            self._load()

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
        self._index = PromptFileIndex.model_validate_json(self._index_path.read_text())
        # Reconstruct the file paths since they're excluded from serialization
        for pf in self._index.files:
            if pf.path is None:
                pf.path = self._path / f"{pf.name}.{pf.version}.jinja"

    def _save(self):
        """Save the prompt index to disk."""
        self._index_path.write_text(self._index.model_dump_json())

    def _scan(self):
        """Scan directory for prompt files and build the index."""
        self._index: PromptFileIndex = PromptFileIndex()
        for path in self._path.glob("*.jinja*"):
            name, version = path.stem.rsplit(".", 1) if "." in path.stem else (path.stem, DEFAULT_VERSION)
            with path.open("r") as f:
                pf = PromptFile(text=f.read(), name=name, version=version, path=path, metadata={})
                self._index.files.append(pf)
        self._index_path.write_text(self._index.model_dump_json())

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
