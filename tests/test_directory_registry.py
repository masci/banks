import os
import time
from pathlib import Path

import pytest

from banks.prompt import Prompt
from banks.registries.directory import DirectoryTemplateRegistry
from banks.registry import TemplateNotFoundError


@pytest.fixture
def populated_dir(tmp_path):
    d = tmp_path / "templates"
    d.mkdir()
    for fp in (Path(__file__).parent / "templates").iterdir():
        with open(d / fp.name, "w") as f:
            f.write(fp.read_text())
    return d


def test_init_from_scratch(populated_dir):
    r = DirectoryTemplateRegistry(populated_dir)
    p = r.get(name="blog")
    assert p.raw.startswith("{# Zero-shot, this is already enough for most topics in english -#}")


def test_init_from_existing_index(populated_dir):
    DirectoryTemplateRegistry(populated_dir)
    # at this point, the index has been created
    r = DirectoryTemplateRegistry(populated_dir)
    assert len(r._index.files) == 6


def test_init_from_existing_index_force(populated_dir):
    r = DirectoryTemplateRegistry(populated_dir)  # creates the index
    # change the directory structure
    f = populated_dir / "blog.jinja"
    os.remove(f)
    # force recreation, the renamed file should be updated in the index
    r = DirectoryTemplateRegistry(populated_dir, force_reindex=True)
    with pytest.raises(TemplateNotFoundError):
        r.get(name="blog")


def test_init_invalid_dir():
    with pytest.raises(ValueError):
        DirectoryTemplateRegistry(Path("does/not/exists"))


def test_get_not_found(populated_dir):
    r = DirectoryTemplateRegistry(populated_dir)
    with pytest.raises(TemplateNotFoundError):
        r.get(name="FOO")


def test_set_existing_no_overwrite(populated_dir):
    r = DirectoryTemplateRegistry(populated_dir)
    new_prompt = Prompt("a new prompt!")
    r.set(name="blog", prompt=new_prompt)  # template already exists, expected to be no-op
    assert r.get(name="blog").raw.startswith("{# Zero-shot, this is already enough for most topics in english -#}")


def test_set_existing_overwrite(populated_dir):
    r = DirectoryTemplateRegistry(populated_dir)
    new_prompt = Prompt("a new prompt!")
    r.set(name="blog", prompt=new_prompt, overwrite=True)
    assert r.get(name="blog").raw.startswith("a new prompt!")


def test_set_multiple_templates(populated_dir):
    r = DirectoryTemplateRegistry(Path("/tmp/banks/templates"))
    new_prompt = Prompt("a very new prompt!")
    old_prompt = Prompt("an old prompt!")
    r.set(name="new", version="2", prompt=new_prompt)
    r.set(name="old", version="1", prompt=old_prompt)
    assert r.get(name="old", version="1").raw == "an old prompt!"
    assert r.get(name="new", version="2").raw == "a very new prompt!"


def test_empty_meta(populated_dir):
    r = DirectoryTemplateRegistry(populated_dir)
    with pytest.raises(FileNotFoundError):
        r.get_meta(name="blog")


def test_set_meta(populated_dir):
    r = DirectoryTemplateRegistry(populated_dir)
    r.set_meta(name="new", version="2", meta={"accuracy": 91.2, "last_updated": time.ctime()})
    assert r.get_meta(name="new", version="2") == {"accuracy": 91.2, "last_updated": time.ctime()}