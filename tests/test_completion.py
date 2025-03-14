from os import getenv
from unittest import mock

import pytest
from jinja2.environment import Environment
from litellm.types.utils import ChatCompletionMessageToolCall, Function

from banks.errors import InvalidPromptError, LLMError
from banks.extensions.completion import CompletionExtension
from banks.types import ChatMessage, Tool


@pytest.fixture
def ext():
    return CompletionExtension(environment=Environment())


@pytest.fixture
def mocked_choices_no_tools():
    return [mock.MagicMock(message=mock.MagicMock(tool_calls=None, content="some response"))]


@pytest.fixture
def mocked_choices_with_tools():
    return [
        mock.MagicMock(
            message=mock.MagicMock(
                tool_calls=[
                    ChatCompletionMessageToolCall(
                        id="call_DN6IiLULWZw7sobV6puCji1O",
                        function=Function(
                            arguments='{"location": "San Francisco", "unit": "celsius"}', name="get_current_weather"
                        ),
                        type="function",
                    ),
                    ChatCompletionMessageToolCall(
                        id="call_ERm1JfYO9AFo2oEWRmWUd40c",
                        function=Function(
                            arguments='{"location": "Tokyo", "unit": "celsius"}', name="get_current_weather"
                        ),
                        type="function",
                    ),
                    ChatCompletionMessageToolCall(
                        id="call_2lvUVB1y4wKunSxTenR0zClP",
                        function=Function(
                            arguments='{"location": "Paris", "unit": "celsius"}', name="get_current_weather"
                        ),
                        type="function",
                    ),
                ],
                content="some response",
            )
        )
    ]


@pytest.fixture
def tools():
    return [
        Tool.model_validate(
            {
                "type": "function",
                "function": {
                    "name": "getenv",
                    "description": "Get an environment variable, return None if it doesn't exist.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "key": {
                                "type": "string",
                                "description": "The name of the environment variable",
                            },
                            "default": {
                                "type": "string",
                                "description": "The value to return if the variable was not found",
                            },
                        },
                        "required": ["key"],
                    },
                },
                "import_path": "os.getenv",
            }
        )
    ]


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


@pytest.mark.asyncio
async def test__do_completion_async_no_prompt(ext):
    with pytest.raises(InvalidPromptError, match="Completion must contain at least one chat message"):
        await ext._do_completion_async("test-model", lambda: " ")


def test__do_completion_no_tools(ext, mocked_choices_no_tools):
    with mock.patch("litellm.completion") as mocked_completion:
        mocked_completion.return_value.choices = mocked_choices_no_tools
        ext._do_completion("test-model", lambda: '{"role":"user", "content":"hello"}')
        mocked_completion.assert_called_with(
            model="test-model", messages=[ChatMessage(role="user", content="hello").model_dump()], tools=None
        )


@pytest.mark.asyncio
async def test__do_completion_async_no_tools(ext, mocked_choices_no_tools):
    with mock.patch("litellm.acompletion") as mocked_completion:
        mocked_completion.return_value.choices = mocked_choices_no_tools
        await ext._do_completion_async("test-model", lambda: '{"role":"user", "content":"hello"}')
        mocked_completion.assert_called_with(
            model="test-model",
            messages=[{"role": "user", "content": "hello", "tool_call_id": None, "name": None}],
            tools=None,
        )


def test__do_completion_with_tools(ext, mocked_choices_with_tools):
    ext._get_tool_callable = mock.MagicMock(return_value=lambda location, unit: f"I got {location} with {unit}")
    ext._body_to_messages = mock.MagicMock(
        return_value=(
            [ChatMessage(role="user", content="message1"), ChatMessage(role="user", content="message2")],
            [mock.MagicMock(), mock.MagicMock()],
        )
    )
    with mock.patch("litellm.completion") as mocked_completion:
        mocked_completion.return_value.choices = mocked_choices_with_tools
        ext._do_completion("test-model", lambda: '{"role":"user", "content":"hello"}')
        calls = mocked_completion.call_args_list
        assert len(calls) == 2  # complete query, complete with tool results
        assert len(calls[0].kwargs["tools"]) == 2
        for m in calls[1].kwargs["messages"]:
            if type(m) is ChatMessage:
                assert m.role == "tool"
                assert m.name == "get_current_weather"


@pytest.mark.asyncio
async def test__do_completion_async_with_tools(ext, mocked_choices_with_tools, tools):
    ext._get_tool_callable = mock.MagicMock(return_value=lambda location, unit: f"I got {location} with {unit}")
    ext._body_to_messages = mock.MagicMock(
        return_value=(
            [ChatMessage(role="user", content="message1"), ChatMessage(role="user", content="message2")],
            tools,
        )
    )
    with mock.patch("litellm.acompletion") as mocked_completion:
        mocked_completion.return_value.choices = mocked_choices_with_tools
        await ext._do_completion_async("test-model", lambda: '{"role":"user", "content":"hello"}')
        calls = mocked_completion.call_args_list
        assert len(calls) == 2  # complete query, complete with tool results
        assert calls[0].kwargs["tools"] == [t.model_dump() for t in tools]
        for m in calls[1].kwargs["messages"]:
            if type(m) is ChatMessage:
                assert m.role == "tool"
                assert m.name == "get_current_weather"


def test__do_completion_with_tools_malformed(ext, mocked_choices_with_tools):
    mocked_choices_with_tools[0].message.tool_calls[0].function.name = None
    with mock.patch("litellm.completion") as mocked_completion:
        mocked_completion.return_value.choices = mocked_choices_with_tools
        with pytest.raises(LLMError):
            ext._do_completion("test-model", lambda: '{"role":"user", "content":"hello"}')


@pytest.mark.asyncio
async def test__do_completion_async_with_tools_malformed(ext, mocked_choices_with_tools):
    mocked_choices_with_tools[0].message.tool_calls[0].function.name = None
    with mock.patch("litellm.acompletion") as mocked_completion:
        mocked_completion.return_value.choices = mocked_choices_with_tools
        with pytest.raises(LLMError):
            await ext._do_completion_async("test-model", lambda: '{"role":"user", "content":"hello"}')


@pytest.mark.asyncio
async def test__do_completion_async_no_prompt_no_tools(ext, mocked_choices_no_tools):
    with mock.patch("litellm.acompletion") as mocked_completion:
        mocked_completion.return_value.choices = mocked_choices_no_tools
        await ext._do_completion_async("test-model", lambda: '{"role":"user", "content":"hello"}')
        mocked_completion.assert_called_with(
            model="test-model",
            messages=[{"role": "user", "content": "hello", "tool_call_id": None, "name": None}],
            tools=None,
        )


def test__get_tool_callable(ext, tools):
    tool_call = mock.MagicMock()

    tool_call.function.name = "getenv"
    assert ext._get_tool_callable(tools, tool_call) == getenv

    tool_call.function.name = "another_func"
    with pytest.raises(ValueError, match="Function another_func not found in available tools"):
        ext._get_tool_callable(tools, tool_call)
