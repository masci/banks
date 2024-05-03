import regex as re
from unittest import mock

from banks import Prompt


def test_canary_word_generation():
    p = Prompt("{{canary_word}}This is my prompt")
    assert re.match(r"BANKS\[.{8}\]This is my prompt", p.text())


def test_canary_word_leaked():
    p = Prompt("{{canary_word}}This is my prompt")
    assert p.canary_leaked(p.text())

    p = Prompt("This is my prompt")
    assert not p.canary_leaked(p.text())


def test_prompt_cache_miss():
    p = Prompt("This is my prompt")
    p.text()
    cached = list(p._cache.values())
    assert len(cached) == 1
    assert cached[0] == "This is my prompt"


def test_prompt_cache_hit():
    p = Prompt("This is my prompt")
    mock_render = mock.MagicMock()
    p._template.render = mock_render
    p.text()
    mock_render.assert_called_once()
    mock_render.reset_mock()
    p.text()
    mock_render.assert_not_called()
