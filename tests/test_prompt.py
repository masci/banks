from unittest import mock

import pytest
import regex as re
from jinja2 import Environment

from banks import AsyncPrompt, Prompt
from banks.cache import DefaultCache
from banks.errors import AsyncError


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


def test_ctor():
    p = Prompt(
        text="This is raw text",
        version="1.0",
        metadata={"LLM": "GPT-3.5"},
        canary_word="FOO",
        render_cache=DefaultCache(),
    )
    assert p.raw == "This is raw text"
    assert p.version == "1.0"
    assert p.metadata == {"LLM": "GPT-3.5"}
    assert p.canary_leaked("The message is FOO")
    assert p.text() == "This is raw text"
    assert p.text() == "This is raw text"


def test_ctor_async_disabled():
    with mock.patch("banks.prompt.config", ASYNC_ENABLED=False):
        with pytest.raises(AsyncError):
            AsyncPrompt(text="This is raw text")


@pytest.mark.asyncio
async def test_ctor_async():
    with mock.patch("banks.prompt.config", ASYNC_ENABLED=True):
        p = AsyncPrompt(
            text="This is raw text",
            version="1.0",
            metadata={"LLM": "GPT-3.5"},
            canary_word="FOO",
            render_cache=DefaultCache(),
        )
        p._template = Environment(autoescape=True, enable_async=True).from_string(p.raw)
        assert p.raw == "This is raw text"
        assert p.version == "1.0"
        assert p.metadata == {"LLM": "GPT-3.5"}
        assert p.canary_leaked("The message is FOO")
        assert await p.text() == "This is raw text"
        assert await p.text() == "This is raw text"
