import pytest

from banks.errors import PromptNotFoundError
from banks.prompt import Prompt
from banks.registries.file import FilePromptRegistry, PromptRegistryIndex
from banks.types import PromptModel


@pytest.fixture
def populated_registry(tmp_path):
    prompt_models = [PromptModel(name="name", version="version", text="prompt")]
    idx = PromptRegistryIndex(prompts=prompt_models)
    with open(tmp_path / "index.json", "w") as f:
        f.write(idx.model_dump_json())
    return FilePromptRegistry(tmp_path / "index.json")


def test_init_from_scratch(tmp_path):
    index_file = tmp_path / "test" / "index.json"
    r = FilePromptRegistry(index_file)
    assert r._index_fpath == index_file
    assert index_file.parent.exists()


def test_init_from_existing_dir(tmp_path):
    r = FilePromptRegistry(tmp_path / "index.json")
    r._save()
    assert r._index_fpath.parent.exists()


def test_init_from_existing_index(populated_registry):
    populated_registry.get(name="name", version="version")


def test_get_not_found(populated_registry):
    with pytest.raises(PromptNotFoundError):
        populated_registry.get(name="name", version="nonexisting_version")


def test_set_existing_no_overwrite(populated_registry):
    new_prompt = "a new prompt!"
    populated_registry.set(prompt=Prompt(new_prompt))  # template already exists, expected to be no-op
    assert populated_registry.get(name="name", version="version").raw == "prompt"


def test_set_existing_overwrite(populated_registry):
    new_prompt = "a new prompt!"
    populated_registry.set(prompt=Prompt(new_prompt, name="name", version="version"), overwrite=True)
    assert populated_registry.get(name="name", version="version").raw == new_prompt


def test_set_new(populated_registry):
    new_prompt = "a new prompt!"
    populated_registry.set(prompt=Prompt(new_prompt, name="name", version="version2"))
    assert populated_registry.get(name="name", version="version").raw == "prompt"
    assert populated_registry.get(name="name", version="version2").raw == new_prompt
