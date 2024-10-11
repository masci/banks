# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
from typing import cast

from jinja2 import TemplateSyntaxError, nodes
from jinja2.ext import Extension
from litellm import acompletion, completion
from litellm.types.utils import ModelResponse
from pydantic import ValidationError

from banks.types import ChatMessage

SUPPORTED_KWARGS = ("model",)


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

    def _do_completion(self, model_name, caller):
        """
        Helper callback.
        """
        messages = self._body_to_messages(caller())
        if not messages:
            return ""

        response = cast(ModelResponse, completion(model=model_name, messages=messages))
        return response.choices[0].message.content  # type: ignore

    async def _do_completion_async(self, model_name, caller):
        """
        Helper callback.
        """
        messages = self._body_to_messages(caller())
        if not messages:
            return ""

        response = cast(ModelResponse, await acompletion(model=model_name, messages=messages))
        return response.choices[0].message.content  # type: ignore

    def _body_to_messages(self, body: str) -> list[ChatMessage]:
        body = body.strip()
        if not body:
            return []

        messages = []
        for line in body.split("\n"):
            try:
                messages.append(ChatMessage.model_validate_json(line))
            except ValidationError:  # pylint: disable=R0801
                pass

        if not messages:
            messages.append(ChatMessage(role="user", content=body))

        return messages
