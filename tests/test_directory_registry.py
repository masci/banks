import os
from pathlib import Path

import pytest

from banks.errors import InvalidPromptError, PromptNotFoundError
from banks.prompt import Prompt
from banks.registries.directory import DEFAULT_INDEX_NAME, DirectoryPromptRegistry, PromptFileIndex


@pytest.fixture
def registry(tmp_path: Path):
    d = tmp_path / "templates"
    d.mkdir()
    for fp in (Path(__file__).parent / "templates").iterdir():
        with open(d / fp.name, "w") as f:
            f.write(fp.read_text())
    return DirectoryPromptRegistry(d, force_reindex=True)


def test_init_from_scratch(registry: DirectoryPromptRegistry):
    p = registry.get(name="blog")
    assert p.raw.startswith("{# Zero-shot, this is already enough for most topics in english -#}")
    assert p.metadata == {}


def test_init_from_existing_index(tmp_path: Path):
    pi = PromptFileIndex()
    idx = tmp_path / DEFAULT_INDEX_NAME
    idx.write_text(pi.model_dump_json())
    r = DirectoryPromptRegistry(tmp_path)
    assert len(r._index.files) == 0


def test_init_from_existing_index_force(registry: DirectoryPromptRegistry):
    # change the directory structure
    f = registry.path / "blog.jinja"
    os.remove(f)
    # force recreation, the renamed file should be updated in the index
    r = DirectoryPromptRegistry(registry.path, force_reindex=True)
    with pytest.raises(PromptNotFoundError):
        r.get(name="blog")


def test_init_invalid_dir():
    with pytest.raises(ValueError):
        DirectoryPromptRegistry(Path("does/not/exists"))


def test_get_not_found(registry: DirectoryPromptRegistry):
    with pytest.raises(PromptNotFoundError):
        registry.get(name="FOO")


def test_set_existing_no_overwrite(registry: DirectoryPromptRegistry):
    new_prompt = Prompt("a new prompt!", name="blog")
    with pytest.raises(
        InvalidPromptError, match=r"Prompt with name 'blog' already exists. Use overwrite=True to overwrite"
    ):
        registry.set(prompt=new_prompt)


def test_set_existing_overwrite(registry: DirectoryPromptRegistry):
    new_prompt = Prompt("a new prompt!", name="blog")
    registry.set(prompt=new_prompt, overwrite=True)
    assert registry.get(name="blog").text() == "a new prompt!"
    assert "created_at" in registry.get(name="blog").metadata  # created_at is added when overwrite==True


def test_set_multiple_templates(registry: DirectoryPromptRegistry):
    new_prompt = Prompt("a very new prompt!", name="new", version="2")
    registry.set(prompt=new_prompt)
    old_prompt = Prompt("an old prompt!", name="old", version="1")
    registry.set(prompt=old_prompt)

    p = registry.get(name="old", version="1")
    assert p.raw == "an old prompt!"
    assert "created_at" in p.metadata

    p = registry.get(name="new", version="2")
    assert p.raw == "a very new prompt!"
    assert "created_at" in p.metadata


def test_update_meta(registry: DirectoryPromptRegistry):
    # test metadata for initial set
    new_prompt = Prompt("a very new prompt!", name="new", version="3", metadata={"accuracy": 91.2})
    registry.set(prompt=new_prompt)
    created_at = new_prompt.metadata["created_at"]
    assert registry.get(name="new", version="3").metadata == {"accuracy": 91.2, "created_at": created_at}

    # test metadata update for existing prompt
    p = registry.get(name="new", version="3")
    created_time = p.metadata["created_at"]
    p.metadata["accuracy"] = 94.3
    registry.set(prompt=p, overwrite=True)
    # reload prompt
    p = registry.get(name="new", version="3")
    assert p.metadata == {"accuracy": 94.3, "created_at": created_time}


@pytest.mark.parametrize(
    ("name", "version"),
    [
        ("../victim/pwned", "0"),
        ("/etc/passwd", "0"),
        ("okay", "../../../evil"),
        ("team/../nested", "0"),
    ],
)
def test_set_rejects_path_escape(tmp_path: Path, name: str, version: str):
    registry_dir = tmp_path / "registry"
    registry_dir.mkdir()
    victim = tmp_path / "victim"
    victim.mkdir()
    reg = DirectoryPromptRegistry(registry_dir, force_reindex=True)

    with pytest.raises(InvalidPromptError):
        reg.set(prompt=Prompt("pwn", name=name, version=version))

    assert list(victim.iterdir()) == []
    assert not (tmp_path / "evil.jinja").exists()


def test_set_rejects_dot_segment_overwrite_bypass(tmp_path: Path):
    registry_dir = tmp_path / "registry"
    registry_dir.mkdir()
    reg = DirectoryPromptRegistry(registry_dir, force_reindex=True)
    (registry_dir / "team").mkdir()

    reg.set(prompt=Prompt("original", name="team/nested", version="1"))

    with pytest.raises(InvalidPromptError):
        reg.set(prompt=Prompt("bypass", name="team/../nested", version="1"))

    assert (registry_dir / "team" / "nested.1.jinja").read_text() == "original"


def test_set_allows_nested_name(tmp_path: Path):
    registry_dir = tmp_path / "registry"
    registry_dir.mkdir()
    reg = DirectoryPromptRegistry(registry_dir, force_reindex=True)
    (registry_dir / "team").mkdir()

    reg.set(prompt=Prompt("nested prompt", name="team/nested", version="1"))
    assert (registry_dir / "team" / "nested.1.jinja").read_text() == "nested prompt"


def test_load_rejects_poisoned_index(tmp_path: Path):
    (tmp_path / DEFAULT_INDEX_NAME).write_text(
        '{"files":[{"text":"pwn","name":"../evil","version":"0","metadata":{}}]}'
    )
    with pytest.raises(InvalidPromptError):
        DirectoryPromptRegistry(tmp_path)
