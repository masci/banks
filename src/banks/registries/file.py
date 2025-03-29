# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
"""
File-based prompt registry implementation that stores all prompts in a single JSON file.

This module provides functionality to store and retrieve prompts using a single JSON file
as the storage backend. The file contains an index of all prompts with their associated
metadata and content.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel

from banks.errors import InvalidPromptError, PromptNotFoundError
from banks.prompt import Prompt, PromptModel


class PromptRegistryIndex(BaseModel):
    """
    Model representing the registry index containing all prompts.

    Stores a list of PromptModel objects that represent all prompts in the registry.
    """

    prompts: list[PromptModel] = []


class FilePromptRegistry:
    """A prompt registry storing all prompt data in a single JSON file."""

    def __init__(self, registry_index: str) -> None:
        """
        Initialize the file prompt registry.

        Args:
            registry_index: Path to the JSON file that will store the prompts

        Note:
            Creates parent directories if they don't exist.
        """
        self._index_fpath: Path = Path(registry_index)
        self._index: PromptRegistryIndex = PromptRegistryIndex(prompts=[])
        try:
            self._index = PromptRegistryIndex.model_validate_json(self._index_fpath.read_text(encoding="utf-8"))
        except FileNotFoundError:
            # init the user data folder
            self._index_fpath.parent.mkdir(parents=True, exist_ok=True)

    def get(self, *, name: str, version: str | None = None) -> Prompt:
        """
        Retrieve a prompt by name and version.

        Args:
            name: Name of the prompt to retrieve
            version: Version of the prompt (optional)

        Returns:
            The requested Prompt object

        Raises:
            PromptNotFoundError: If the requested prompt doesn't exist
        """
        _, model = self._get_prompt_model(name, version)
        return Prompt(**model.model_dump())

    def set(self, *, prompt: Prompt, overwrite: bool = False) -> None:
        """
        Store a prompt in the registry.

        Args:
            prompt: The Prompt object to store
            overwrite: Whether to overwrite an existing prompt

        Raises:
            InvalidPromptError: If prompt exists and overwrite=False
        """
        try:
            idx, p_model = self._get_prompt_model(prompt.name, prompt.version)
            if overwrite:
                self._index.prompts[idx] = PromptModel.from_prompt(prompt)
                self._save()
            else:
                msg = f"Prompt with name '{prompt.name}' already exists. Use overwrite=True to overwrite"
                raise InvalidPromptError(msg)
        except PromptNotFoundError:
            p_model = PromptModel.from_prompt(prompt)
            self._index.prompts.append(p_model)
            self._save()

    def _save(self) -> None:
        """
        Save the prompt index to the JSON file.

        Writes the current state of the registry to disk.
        """
        with open(self._index_fpath, "w", encoding="utf-8") as f:
            f.write(self._index.model_dump_json())

    def _get_prompt_model(self, name: str | None, version: str | None) -> tuple[int, PromptModel]:
        """
        Find a prompt model in the index by name and version.

        Args:
            name: Name of the prompt
            version: Version of the prompt

        Returns:
            Tuple of (index position, PromptModel)

        Raises:
            PromptNotFoundError: If the prompt doesn't exist in the index
        """
        for i, model in enumerate(self._index.prompts):
            if model.name == name and model.version == version:
                return i, model

        msg = f"cannot find prompt with name '{name}' and version '{version}'"
        raise PromptNotFoundError(msg)
