# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
from pathlib import Path

from pydantic import BaseModel

from banks.errors import InvalidPromptError, PromptNotFoundError
from banks.prompt import Prompt, PromptModel


class PromptRegistryIndex(BaseModel):
    prompts: list[PromptModel] = []


class FilePromptRegistry:
    """A prompt registry storing all the prompt data in a single JSON file."""

    def __init__(self, registry_index: Path) -> None:
        """Creates an instance of the File Prompt Registry.

        Args:
            registry_index: The path to the index file.
        """
        self._index_fpath: Path = registry_index
        self._index: PromptRegistryIndex = PromptRegistryIndex(prompts=[])
        try:
            self._index = PromptRegistryIndex.model_validate_json(self._index_fpath.read_text())
        except FileNotFoundError:
            # init the user data folder
            self._index_fpath.parent.mkdir(parents=True, exist_ok=True)

    def get(self, *, name: str, version: str | None = None) -> Prompt:
        _, model = self._get_prompt_model(name, version)
        return Prompt(**model.model_dump())

    def set(self, *, prompt: Prompt, overwrite: bool = False) -> None:
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
        with open(self._index_fpath, "w", encoding="locale") as f:
            f.write(self._index.model_dump_json())

    def _get_prompt_model(self, name: str | None, version: str | None) -> tuple[int, PromptModel]:
        for i, model in enumerate(self._index.prompts):
            if model.name == name and model.version == version:
                return i, model

        msg = f"cannot find prompt with name '{name}' and version '{version}'"
        raise PromptNotFoundError(msg)
