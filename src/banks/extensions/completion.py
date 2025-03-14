# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
import importlib
import json
from typing import cast

from jinja2 import TemplateSyntaxError, nodes
from jinja2.ext import Extension
from pydantic import ValidationError

from banks.errors import InvalidPromptError, LLMError
from banks.types import ChatMessage, Tool

SUPPORTED_KWARGS = ("model",)
LITELLM_INSTALL_MSG = "litellm is not installed. Please install it with `pip install litellm`."


class CompletionExtension(Extension):
    """
    `completion` can be used to send to the LLM the content of the block in form of messages.

    The rendered value of the block can be used as is but it's usually more useful to
    assign it to a variable and access it from another section of the prompt.

    Example:
        ```
        {% set response %}
        {% completion model="gpt-3.5-turbo-0125" %}
        {% chat role="user" %}You are a helpful assistant{% endchat %}
        {% endcompletion %}
        {% endset %}

        {# output the response content #}
        {{ response }}
        ```
    """

    # a set of names that trigger the extension.
    tags = {"completion"}  # noqa

    def parse(self, parser):
        # We get the line number of the first token for error reporting
        lineno = next(parser.stream).lineno

        # Gather tokens up to the next block_end ('%}')
        gathered = []
        while parser.stream.current.type != "block_end":
            gathered.append(next(parser.stream))

        # If all has gone well, we will have one triplet of tokens:
        #   (type='name', value='model'),
        #   (type='assign', value='='),
        #   (type='string', value='gpt-3.5-turbo-0125'),
        # Anything else is a parse error
        error_msg = f"Invalid syntax for completion: {gathered}"
        try:
            attr_name, attr_assign, attr_value = gathered  # pylint: disable=unbalanced-tuple-unpacking
        except ValueError:
            raise TemplateSyntaxError(error_msg, lineno) from None

        # Validate tag attributes
        if attr_name.value not in SUPPORTED_KWARGS or attr_assign.value != "=":
            raise TemplateSyntaxError(error_msg, lineno)

        # Pass the role name to the CallBlock node
        args: list[nodes.Expr] = [nodes.Const(attr_value.value)]

        # Message body
        body = parser.parse_statements(("name:endcompletion",), drop_needle=True)

        # Call LLM
        if parser.environment.is_async:
            return nodes.CallBlock(self.call_method("_do_completion_async", args), [], [], body).set_lineno(lineno)
        return nodes.CallBlock(self.call_method("_do_completion", args), [], [], body).set_lineno(lineno)

    def _get_tool_callable(self, tools, tool_call):
        for tool in tools:
            if tool.function.name == tool_call.function.name:
                module_name, func_name = tool.import_path.rsplit(".", maxsplit=1)
                module = importlib.import_module(module_name)
                return getattr(module, func_name)
        msg = f"Function {tool_call.function.name} not found in available tools"
        raise ValueError(msg)

    def _do_completion(self, model_name, caller):
        """
        Helper callback.
        """
        try:
            from litellm import completion
            from litellm.types.utils import Choices, ModelResponse
        except ImportError as e:
            raise ImportError(LITELLM_INSTALL_MSG) from e

        messages, tools = self._body_to_messages(caller())
        message_dicts = [m.model_dump() for m in messages]
        tool_dicts = [t.model_dump() for t in tools] or None

        response = cast(ModelResponse, completion(model=model_name, messages=message_dicts, tools=tool_dicts))
        choices = cast(list[Choices], response.choices)
        tool_calls = choices[0].message.tool_calls
        if not tool_calls:
            return choices[0].message.content

        message_dicts.append(choices[0].message.model_dump())
        for tool_call in tool_calls:
            if not tool_call.function.name:
                msg = "Malformed response: function name is empty"
                raise LLMError(msg)

            func = self._get_tool_callable(tools, tool_call)

            function_args = json.loads(tool_call.function.arguments)
            function_response = func(**function_args)
            message_dicts.append(
                ChatMessage(
                    tool_call_id=tool_call.id, role="tool", name=tool_call.function.name, content=function_response
                ).model_dump()
            )

        response = cast(ModelResponse, completion(model=model_name, messages=message_dicts, tools=tool_dicts))
        choices = cast(list[Choices], response.choices)
        return choices[0].message.content

    async def _do_completion_async(self, model_name, caller):
        """
        Helper callback.
        """
        try:
            from litellm import acompletion
            from litellm.types.utils import Choices, ModelResponse
        except ImportError as e:
            raise ImportError(LITELLM_INSTALL_MSG) from e

        messages, tools = self._body_to_messages(caller())
        message_dicts = [m.model_dump() for m in messages]
        tool_dicts = [t.model_dump() for t in tools] or None

        response = cast(ModelResponse, await acompletion(model=model_name, messages=message_dicts, tools=tool_dicts))
        choices = cast(list[Choices], response.choices)
        tool_calls = choices[0].message.tool_calls or []
        if not tool_calls:
            return choices[0].message.content

        message_dicts.append(choices[0].message.model_dump())
        for tool_call in tool_calls:
            if not tool_call.function.name:
                msg = "Function name is empty"
                raise LLMError(msg)

            func = self._get_tool_callable(tools, tool_call)

            message_dicts.append(
                ChatMessage(
                    tool_call_id=tool_call.id,
                    role="tool",
                    name=tool_call.function.name,
                    content=func(**json.loads(tool_call.function.arguments)),
                ).model_dump()
            )

        response = cast(ModelResponse, await acompletion(model=model_name, messages=message_dicts, tools=tool_dicts))
        choices = cast(list[Choices], response.choices)
        return choices[0].message.content

    def _body_to_messages(self, body: str) -> tuple[list[ChatMessage], list[Tool]]:
        """Converts each line in the body of a block into a chat message."""
        body = body.strip()
        messages = []
        tools = []
        for line in body.split("\n"):
            try:
                # Try to parse a chat message
                messages.append(ChatMessage.model_validate_json(line))
            except ValidationError:  # pylint: disable=R0801
                try:
                    # If not a chat message, try to parse a tool
                    tools.append(Tool.model_validate_json(line))
                except ValidationError:
                    # Give up
                    pass

        if not messages:
            msg = "Completion must contain at least one chat message"
            raise InvalidPromptError(msg)

        return (messages, tools)
