import pytest
import redis


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
