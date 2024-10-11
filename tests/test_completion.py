from unittest import mock

import pytest
from jinja2.environment import Environment

from banks.extensions.completion import CompletionExtension
from banks.types import ChatMessage


@pytest.fixture
def ext():
    return CompletionExtension(environment=Environment())


def test__body_to_messages(ext):
    assert ext._body_to_messages(" ") == []
    assert ext._body_to_messages(' \n{"role":"user", "content":"hello"}') == [ChatMessage(role="user", content="hello")]
    assert ext._body_to_messages(" \nhello\n ") == [ChatMessage(role="user", content="hello")]
    assert ext._body_to_messages('{"role":"user", "content":"hello"}\n HELLO!') == [
        ChatMessage(role="user", content="hello")
    ]


def test__do_completion(ext):
    assert ext._do_completion("test-model", lambda: " ") == ""
    with mock.patch("banks.extensions.completion.completion") as mocked_completion:
        ext._do_completion("test-model", lambda: "hello")
        mocked_completion.assert_called_with(model="test-model", messages=[ChatMessage(role="user", content="hello")])


@pytest.mark.asyncio
async def test__do_completion_async(ext):
    assert await ext._do_completion_async("test-model", lambda: " ") == ""
    with mock.patch("banks.extensions.completion.acompletion") as mocked_completion:
        await ext._do_completion_async("test-model", lambda: "hello")
        mocked_completion.assert_called_with(model="test-model", messages=[ChatMessage(role="user", content="hello")])
