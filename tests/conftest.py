from pathlib import Path

import pytest
import redis

from banks.env import env
from banks.types import CONTENT_BLOCK_END, content_block_start
from banks.utils import SENTINEL_VAR


def is_redis_available():
    try:
        redis.Redis(host="localhost", port=6379).ping()
        return True
    except redis.ConnectionError:
        return False


def pytest_configure(config):
    config.addinivalue_line("markers", "redis: mark test as requiring Redis")


@pytest.fixture(autouse=True)
def skip_by_redis(request):
    if request.node.get_closest_marker("redis"):
        if not is_redis_available():
            pytest.skip("Redis is not available")


@pytest.fixture
def data_path() -> Path:
    here = Path(__file__).parent
    return here / "data"


@pytest.fixture
def sentinel() -> str:
    """A known stand-in for the random per-Prompt sentinel, to keep assertions readable."""
    return "test-sentinel:"


@pytest.fixture
def jinja_context(sentinel):
    """A render context carrying `sentinel`, as filters and extensions receive at render time."""
    return env.from_string("").new_context({SENTINEL_VAR: sentinel})


@pytest.fixture
def unwrap_content_block(sentinel):
    """Return the JSON payload a media filter wrapped in content block markers."""
    start = content_block_start(sentinel)

    def _unwrap(rendered: str) -> str:
        assert rendered.startswith(start)
        assert rendered.endswith(CONTENT_BLOCK_END)
        return rendered[len(start) : -len(CONTENT_BLOCK_END)]

    return _unwrap
