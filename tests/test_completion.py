from unittest import mock

import pytest
from jinja2.environment import Environment

from banks.errors import InvalidPromptError
from banks.extensions.completion import CompletionExtension
from banks.types import ChatMessage


@pytest.fixture
def ext():
    return CompletionExtension(environment=Environment())


@pytest.fixture
def mocked_choices_no_tools():
    return [mock.MagicMock(message=mock.MagicMock(tool_calls=None, content="some response"))]


def test__body_to_messages(ext):
    assert ext._body_to_messages(' \n{"role":"user", "content":"hello"}') == (
        [ChatMessage(role="user", content="hello")],
        [],
    )
    assert ext._body_to_messages('{"role":"user", "content":"hello"}\n HELLO!') == (
        [ChatMessage(role="user", content="hello")],
        [],
    )
    with pytest.raises(InvalidPromptError, match="Completion must contain at least one chat message"):
        ext._body_to_messages(" ")
    with pytest.raises(InvalidPromptError, match="Completion must contain at least one chat message"):
        ext._body_to_messages(" \nhello\n ")


def test__do_completion_no_prompt(ext):
    with pytest.raises(InvalidPromptError, match="Completion must contain at least one chat message"):
        ext._do_completion("test-model", lambda: " ")


def test__do_completion_no_tools(ext, mocked_choices_no_tools):
    with mock.patch("banks.extensions.completion.completion") as mocked_completion:
        mocked_completion.return_value.choices = mocked_choices_no_tools
        ext._do_completion("test-model", lambda: '{"role":"user", "content":"hello"}')
        mocked_completion.assert_called_with(
            model="test-model", messages=[ChatMessage(role="user", content="hello")], tools=[]
        )


@pytest.mark.asyncio
async def test__do_completion_async_no_prompt(ext):
    with pytest.raises(InvalidPromptError, match="Completion must contain at least one chat message"):
        await ext._do_completion_async("test-model", lambda: " ")


@pytest.mark.asyncio
async def test__do_completion_async_no_prompt_no_tools(ext, mocked_choices_no_tools):
    with mock.patch("banks.extensions.completion.acompletion") as mocked_completion:
        mocked_completion.return_value.choices = mocked_choices_no_tools
        await ext._do_completion_async("test-model", lambda: '{"role":"user", "content":"hello"}')
        mocked_completion.assert_called_with(
            model="test-model", messages=[ChatMessage(role="user", content="hello")], tools=[]
        )
