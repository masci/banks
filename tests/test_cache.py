import pytest

from banks.cache import DefaultCache


@pytest.fixture
def cache():
    return DefaultCache()


@pytest.mark.parametrize(
    "context_value",
    [{}, {"foo": "bar"}],
)
def test_default_cache_set(context_value, cache):
    cache.set(context_value, "My prompt")
    assert len(cache._cache) == 1
    assert next(iter(cache._cache.values())) == "My prompt"


def test_default_cache_get(cache):
    cache.set({"foo": "bar"}, "My prompt")
    assert cache.get({"foo": "bar"}) == "My prompt"
    assert cache.get({"bar"}) is None


def test_default_cache_clear(cache):
    cache.set({"foo": "bar"}, "My prompt")
    cache.clear()
    assert not len(cache._cache)
