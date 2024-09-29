import os
import time
from pathlib import Path

import pytest

from banks.errors import InvalidPromptError, PromptNotFoundError
from banks.prompt import Prompt
from banks.registries.directory import DirectoryTemplateRegistry


@pytest.fixture
def registry(tmp_path: Path):
    d = tmp_path / "templates"
    d.mkdir()
    for fp in (Path(__file__).parent / "templates").iterdir():
        with open(d / fp.name, "w") as f:
            f.write(fp.read_text())
    return DirectoryTemplateRegistry(d, force_reindex=True)


def test_init_from_scratch(registry: DirectoryTemplateRegistry):
    p = registry.get(name="blog")
    assert p.raw.startswith("{# Zero-shot, this is already enough for most topics in english -#}")
    assert p.metadata == {}


def test_init_from_existing_index(registry: DirectoryTemplateRegistry):
    # at this point, the index has been created
    assert len(registry._index.files) == 6


def test_init_from_existing_index_force(registry: DirectoryTemplateRegistry):
    # change the directory structure
    f = registry.path / "blog.jinja"
    os.remove(f)
    # force recreation, the renamed file should be updated in the index
    r = DirectoryTemplateRegistry(registry.path, force_reindex=True)
    with pytest.raises(PromptNotFoundError):
        r.get(name="blog")


def test_init_invalid_dir():
    with pytest.raises(ValueError):
        DirectoryTemplateRegistry(Path("does/not/exists"))


def test_get_not_found(registry: DirectoryTemplateRegistry):
    with pytest.raises(PromptNotFoundError):
        registry.get(name="FOO")


def test_set_existing_no_overwrite(registry: DirectoryTemplateRegistry):
    new_prompt = Prompt("a new prompt!", name="blog")
    with pytest.raises(
        InvalidPromptError, match="Prompt with name 'blog' already exists. Use overwrite=True to overwrite"
    ):
        registry.set(prompt=new_prompt)


def test_set_existing_overwrite(registry: DirectoryTemplateRegistry):
    new_prompt = Prompt("a new prompt!", name="blog")
    current_time = time.ctime()
    registry.set(prompt=new_prompt, overwrite=True)
    assert registry.get(name="blog").text() == "a new prompt!"
    assert registry.get(name="blog").metadata == {
        "created_at": current_time
    }  # created_at changes because it's overwritten


def test_set_multiple_templates(registry: DirectoryTemplateRegistry):
    current_time = time.ctime()

    new_prompt = Prompt("a very new prompt!", name="new", version="2")
    registry.set(prompt=new_prompt)
    old_prompt = Prompt("an old prompt!", name="old", version="1")
    registry.set(prompt=old_prompt)

    p = registry.get(name="old", version="1")
    assert p.raw == "an old prompt!"
    assert p.metadata == {"created_at": current_time}

    p = registry.get(name="new", version="2")
    assert p.raw == "a very new prompt!"
    assert p.metadata == {"created_at": current_time}


def test_update_meta(registry: DirectoryTemplateRegistry):
    # test metadata for initial set
    new_prompt = Prompt("a very new prompt!", name="new", version="3", metadata={"accuracy": 91.2})
    current_time = time.ctime()
    registry.set(prompt=new_prompt)
    assert registry.get(name="new", version="3").metadata == {"accuracy": 91.2, "created_at": current_time}

    # test metadata update for existing prompt
    p = registry.get(name="new", version="3")
    created_time = p.metadata["created_at"]
    p.metadata["accuracy"] = 94.3
    registry.set(prompt=p, overwrite=True)
    # reload prompt
    p = registry.get(name="new", version="3")
    assert p.metadata == {"accuracy": 94.3, "created_at": created_time}
