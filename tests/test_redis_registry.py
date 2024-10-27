# banks/tests/test_redis_registry.py
import pytest
import redis

from banks.errors import InvalidPromptError, PromptNotFoundError
from banks.prompt import Prompt
from banks.registries.redis import RedisPromptRegistry


@pytest.fixture
def redis_client():
    client = redis.Redis(host="localhost", port=6379, db=0)
    # Clear test database before each test
    client.flushdb()
    return client


@pytest.fixture
def registry(redis_client):  # type: ignore[ARG001]
    return RedisPromptRegistry(redis_url="redis://localhost:6379")


@pytest.mark.redis
def test_get_not_found(registry):
    with pytest.raises(PromptNotFoundError):
        registry.get(name="nonexistent")


@pytest.mark.redis
def test_set_and_get_prompt(registry):
    prompt = Prompt("Hello {{name}}!", name="greeting")
    registry.set(prompt=prompt)

    retrieved = registry.get(name="greeting")
    assert retrieved.raw == "Hello {{name}}!"
    assert retrieved.name == "greeting"
    assert retrieved.version == "0"  # default version
    assert retrieved.metadata == {}


@pytest.mark.redis
def test_set_existing_no_overwrite(registry):
    prompt = Prompt("Hello {{name}}!", name="greeting")
    registry.set(prompt=prompt)

    new_prompt = Prompt("Hi {{name}}!", name="greeting")
    with pytest.raises(
        InvalidPromptError, match="Prompt with name 'greeting' already exists. Use overwrite=True to overwrite"
    ):
        registry.set(prompt=new_prompt)


@pytest.mark.redis
def test_set_existing_overwrite(registry):
    prompt = Prompt("Hello {{name}}!", name="greeting")
    registry.set(prompt=prompt)

    new_prompt = Prompt("Hi {{name}}!", name="greeting")
    registry.set(prompt=new_prompt, overwrite=True)

    retrieved = registry.get(name="greeting")
    assert retrieved.raw == "Hi {{name}}!"


@pytest.mark.redis
def test_set_multiple_versions(registry):
    prompt_v1 = Prompt("Version 1", name="multi", version="1")
    prompt_v2 = Prompt("Version 2", name="multi", version="2")

    registry.set(prompt=prompt_v1)
    registry.set(prompt=prompt_v2)

    retrieved_v1 = registry.get(name="multi", version="1")
    assert retrieved_v1.raw == "Version 1"

    retrieved_v2 = registry.get(name="multi", version="2")
    assert retrieved_v2.raw == "Version 2"


@pytest.mark.redis
def test_get_with_version(registry):
    prompt = Prompt("Test {{var}}", name="test", version="1.0")
    registry.set(prompt=prompt)

    retrieved = registry.get(name="test", version="1.0")
    assert retrieved.version == "1.0"
    assert retrieved.raw == "Test {{var}}"


@pytest.mark.redis
def test_set_with_metadata(registry):
    prompt = Prompt("Test prompt", name="test", metadata={"author": "John", "category": "test"})
    registry.set(prompt=prompt)

    retrieved = registry.get(name="test")
    assert retrieved.metadata == {"author": "John", "category": "test"}


@pytest.mark.redis
def test_update_metadata(registry):
    # Initial prompt with metadata
    prompt = Prompt("Test prompt", name="test", metadata={"score": 90})
    registry.set(prompt=prompt)

    # Update metadata
    updated_prompt = registry.get(name="test")
    updated_prompt.metadata["score"] = 95
    registry.set(prompt=updated_prompt, overwrite=True)

    # Verify update
    retrieved = registry.get(name="test")
    assert retrieved.metadata["score"] == 95


@pytest.mark.redis
def test_invalid_redis_connection():
    with pytest.raises(redis.ConnectionError):
        registry = RedisPromptRegistry(redis_url="redis://nonexistent:6379")
        registry.get(name="test")


@pytest.mark.redis
def test_custom_prefix(redis_client):
    registry = RedisPromptRegistry(redis_url="redis://localhost:6379", prefix="custom:prefix:")

    prompt = Prompt("Test", name="test")
    registry.set(prompt=prompt)

    # Verify the key in Redis has the custom prefix
    key = "custom:prefix:test:0"
    assert redis_client.exists(key)
