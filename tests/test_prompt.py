from unittest import mock

import regex as re

from banks import Prompt
from banks.cache import DefaultCache


def test_canary_word_generation():
    p = Prompt("{{canary_word}}This is my prompt")
    assert re.match(r"BANKS\[.{8}\]This is my prompt", p.text())


def test_canary_word_leaked():
    p = Prompt("{{canary_word}}This is my prompt")
    assert p.canary_leaked(p.text())

    p = Prompt("This is my prompt")
    assert not p.canary_leaked(p.text())


def test_prompt_cache():
    mock_cache = DefaultCache()
    mock_cache.set = mock.Mock()
    p = Prompt("This is my prompt", render_cache=mock_cache)
    p.text()
    mock_cache.set.assert_called_once()
