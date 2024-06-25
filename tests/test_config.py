from pathlib import Path

from platformdirs import user_data_path

from banks.config import _BanksConfig


def test_config_defaults():
    c = _BanksConfig()
    assert c.ASYNC_ENABLED is False
    assert c.USER_DATA_PATH == user_data_path("banks")


def test_config_env_override(monkeypatch):
    c = _BanksConfig()
    monkeypatch.setenv("BANKS_ASYNC_ENABLED", "true")
    assert c.ASYNC_ENABLED is True
    monkeypatch.setenv("BANKS_ASYNC_ENABLED", "false")
    assert c.ASYNC_ENABLED is False
    monkeypatch.setenv("BANKS_USER_DATA_PATH", "/")
    assert c.USER_DATA_PATH == Path("/")

    class TestConfig(_BanksConfig):
        FOO: int = 0

    c = TestConfig()
    assert c.FOO == 0
    monkeypatch.setenv("BANKS_FOO", "42")
    assert c.FOO == 42


def test_config_env_prefix(monkeypatch):
    c = _BanksConfig("BANKS_TEST_")
    monkeypatch.setenv("BANKS_ASYNC_ENABLED", "true")
    assert c.ASYNC_ENABLED is False
    monkeypatch.setenv("BANKS_TEST_ASYNC_ENABLED", "true")
    assert c.ASYNC_ENABLED is True
