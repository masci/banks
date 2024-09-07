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
    p = r.get_prompt(name="blog")
    assert p.raw.startswith("{# Zero-shot, this is already enough for most topics in english -#}")
    assert r.get_meta(name="blog") == {}


def test_init_from_existing_index(populated_dir):
    DirectoryTemplateRegistry(populated_dir)
    # at this point, the index has been created
    r = DirectoryTemplateRegistry(populated_dir)
    assert len(r._index.files) == 6


def test_init_from_existing_index_force(populated_dir):
    _ = DirectoryTemplateRegistry(populated_dir)  # creates the index
    # change the directory structure
    f = populated_dir / "blog.jinja"
    os.remove(f)
    # force recreation, the renamed file should be updated in the index
    r = DirectoryTemplateRegistry(populated_dir, force_reindex=True)
    with pytest.raises(TemplateNotFoundError):
        r.get_prompt(name="blog")
    with pytest.raises(TemplateNotFoundError):
        r.get(name="blog")


def test_init_invalid_dir():
    with pytest.raises(ValueError):
        DirectoryTemplateRegistry(Path("does/not/exists"))


def test_get_not_found(populated_dir):
    r = DirectoryTemplateRegistry(populated_dir)
    with pytest.raises(TemplateNotFoundError):
        r.get_prompt(name="FOO")
    with pytest.raises(TemplateNotFoundError):
        r.get_meta(name="FOO")


def test_set_existing_no_overwrite(populated_dir):
    r = DirectoryTemplateRegistry(populated_dir)
    new_prompt = Prompt("a new prompt!")
    with pytest.raises(ValueError) as e:
        r.set(name="blog", prompt=new_prompt)
    assert "already exists. Use overwrite=True to overwrite." in str(e.value)


def test_set_existing_overwrite(populated_dir):
    r = DirectoryTemplateRegistry(populated_dir)
    new_prompt = Prompt("a new prompt!")
    current_time = time.ctime()
    r.set(name="blog", prompt=new_prompt, overwrite=True)
    assert r.get(name="blog").path.read_text() == "a new prompt!"
    assert r.get_prompt(name="blog").raw.startswith("a new prompt!")
    assert r.get(name="blog").meta == {"created_at": current_time}
    assert r.get_meta(name="blog") == {"created_at": current_time}  # created_at changes because it's overwritten


def test_set_multiple_templates(populated_dir):
    r = DirectoryTemplateRegistry(Path(populated_dir))
    current_time = time.ctime()
    new_prompt = Prompt("a very new prompt!")
    old_prompt = Prompt("an old prompt!")
    r.set(name="new", version="2", prompt=new_prompt)
    r.set(name="old", version="1", prompt=old_prompt)
    assert r.get_prompt(name="old", version="1").raw == "an old prompt!"
    assert r.get_meta(name="old", version="1") == {"created_at": current_time}
    assert r.get_prompt(name="new", version="2").raw == "a very new prompt!"
    assert r.get_meta(name="new", version="2") == {"created_at": current_time}


def test_update_meta(populated_dir):
    r = DirectoryTemplateRegistry(populated_dir)

    # test metadata for initial set
    new_prompt = Prompt("a very new prompt!")
    current_time = time.ctime()
    r.set(name="new", version="3", prompt=new_prompt, meta={"accuracy": 91.2})
    assert r.get_meta(name="new", version="3") == {"accuracy": 91.2, "created_at": current_time}

    # test metadata error update for non-existing prompt
    with pytest.raises(ValueError) as e:
        _ = r.update_meta(name="foo", version="bar", meta={"accuracy": 91.2, "created_at": current_time})
    assert "Cannot set meta for a non-existing prompt." in str(e.value)

    # test metadata update for existing prompt
    created_time = r.get_meta(name="new", version="3")["created_at"]
    _ = r.update_meta(name="new", version="3", meta={"accuracy": 94.3, "created_at": created_time})
    assert r.get_meta(name="new", version="3") == {"accuracy": 94.3, "created_at": created_time}
