from pathlib import Path
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
        name="test_prompt",
        canary_word="FOO",
        render_cache=DefaultCache(),
    )
    assert p.raw == "This is raw text"
    assert p.version == "1.0"
    assert p.metadata == {"LLM": "GPT-3.5"}
    assert p.name == "test_prompt"
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


def test__get_context():
    p = Prompt(text="This is raw text")
    assert p._get_context(None) == p.defaults
    data = {"foo": 42}
    assert p._get_context(data) == data | p.defaults


def test_chat_messages():
    p_file = Path(__file__).parent / "templates" / "chat.jinja"
    p = Prompt(p_file.read_text())

    assert (
        p.text()
        == """
{"role":"system","content":[{"type":"text","text":"You are a helpful assistant."}]}

{"role":"user","content":[{"type":"text","cache_control":{"type":"ephemeral"},"text":"Hello, <bold>how are you?</bold>"}]}

{"role":"system","content":[{"type":"text","text":"I'm doing well, thank you! How can I assist you today?"}]}

{"role":"user","content":[{"type":"text","text":"Can you explain quantum computing?"}]}

Some random text.
""".strip()
    )

    messages = p.chat_messages()
    assert len(messages) == 4
    assert messages[3].role == "user"
    assert messages[3].content[0].text == "Can you explain quantum computing?"


def test_chat_messages_cached():
    mock_cache = DefaultCache()
    mock_cache.set = mock.Mock()
    p_file = Path(__file__).parent / "templates" / "chat.jinja"
    p = Prompt(p_file.read_text(), render_cache=mock_cache)
    p.chat_messages()
    mock_cache.set.assert_called_once()


def test_chat_message_no_chat_tag():
    text = "This is raw text"
    p = Prompt(text=text)
    assert len(p.chat_messages()) == 1
    assert len(p.chat_messages()[0].content) == 1
    assert p.chat_messages()[0].content[0].type == "text"
    assert p.chat_messages()[0].content[0].text == "This is raw text"


def test_variables():
    prompt_text = "This is a {{ first_variable.content }} and this is {{ another_variable }}"
    p = Prompt(text=prompt_text)
    assert p.variables == {"another_variable", "first_variable"}
