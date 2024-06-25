import pytest

from banks.prompt import Prompt
from banks.registries.file import FileTemplateRegistry, PromptTemplate, PromptTemplateIndex
from banks.registry import InvalidTemplateError, TemplateNotFoundError


@pytest.fixture
def populated_index_dir(tmp_path):
    tpls = [PromptTemplate(id="name:version", name="name", version="version", prompt="prompt")]
    idx = PromptTemplateIndex(templates=tpls)
    with open(tmp_path / "index.json", "w") as f:
        f.write(idx.model_dump_json())
    return tmp_path


def test_init_from_scratch(tmp_path):
    index_dir = tmp_path / "test"
    r = FileTemplateRegistry(index_dir)
    assert r._index_fpath == index_dir / "index.json"
    assert index_dir.exists()


def test_init_from_existing_dir(tmp_path):
    r = FileTemplateRegistry(tmp_path)
    r.save()
    assert r._index_fpath.exists()


def test_init_from_existing_index(populated_index_dir):
    r = FileTemplateRegistry(populated_index_dir)
    r.get("name", "version")


def test_make_id():
    assert FileTemplateRegistry._make_id("name", "version") == "name:version"
    assert FileTemplateRegistry._make_id("name", None) == "name"
    with pytest.raises(InvalidTemplateError, match="Template name cannot contain ':'"):
        _ = FileTemplateRegistry._make_id("name:version", None)


def test_get(populated_index_dir):
    r = FileTemplateRegistry(populated_index_dir)
    tpl = r._get_template(FileTemplateRegistry._make_id("name", "version"))
    assert tpl.id == "name:version"


def test_get_not_found(populated_index_dir):
    r = FileTemplateRegistry(populated_index_dir)
    with pytest.raises(TemplateNotFoundError):
        r.get("name", "nonexisting_version")


def test_set_existing_no_overwrite(populated_index_dir):
    r = FileTemplateRegistry(populated_index_dir)
    new_prompt = "a new prompt!"
    r.set(name="name", prompt=Prompt(new_prompt), version="version")  # template already exists, expected to be no-op
    assert r.get("name", "version").raw == "prompt"


def test_set_existing_overwrite(populated_index_dir):
    r = FileTemplateRegistry(populated_index_dir)
    new_prompt = "a new prompt!"
    r.set(name="name", prompt=Prompt(new_prompt), version="version", overwrite=True)
    assert r.get("name", "version").raw == new_prompt


def test_set_new(populated_index_dir):
    r = FileTemplateRegistry(populated_index_dir)
    new_prompt = "a new prompt!"
    r.set(name="name", prompt=Prompt(new_prompt), version="version2")
    assert r.get("name", "version").raw == "prompt"
    assert r.get("name", "version2").raw == new_prompt
