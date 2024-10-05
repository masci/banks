# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
from html.parser import HTMLParser

from jinja2 import TemplateSyntaxError, nodes
from jinja2.ext import Extension

from banks.types import ChatMessage, ChatMessageContent, ContentBlock, ContentBlockType

SUPPORTED_TYPES = ("system", "user")


# This function exists for documentation purpose.
def chat(role: str):  # pylint: disable=W0613
    """
    Text inside `chat` tags will be rendered as JSON strings representing chat messages. Calling `Prompt.chat_messages`
    will return a list of `ChatMessage` instances.

    Example:
        ```
        {% chat role="system" %}
        You are a helpful assistant.
        {% endchat %}

        {% chat role="user" %}
        Hello, how are you?
        {% endchat %}
        ```
    """


class _ContentBlockParser(HTMLParser):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._parse_block_content = False
        self._content_blocks: ChatMessageContent = []

    @property
    def content(self) -> ChatMessageContent:
        return self._content_blocks

    def handle_starttag(self, tag, attrs):
        if tag == "content_block_txt":
            self._parse_block_content = True

    def handle_endtag(self, tag):
        if tag == "content_block_txt":
            self._parse_block_content = False

    def handle_data(self, data):
        if self._parse_block_content:
            self._content_blocks.append(ContentBlock.model_validate_json(data))
        else:
            self._content_blocks.append(ContentBlock(type=ContentBlockType.text, text=data))


class ChatExtension(Extension):
    """
    `chat` can be used to render prompt text as structured ChatMessage objects.

    Example:
        ```
        {% chat role="system" %}
        You are a helpful assistant.
        {% endchat %}
        ```
    """

    # a set of names that trigger the extension.
    tags = {"chat"}  # noqa

    def parse(self, parser):
        # We get the line number of the first token for error reporting
        lineno = next(parser.stream).lineno

        # Gather tokens up to the next block_end ('%}')
        gathered = []
        while parser.stream.current.type != "block_end":
            gathered.append(next(parser.stream))

        # If all has gone well, we will have one triplet of tokens:
        #   (type='name, value='role'),
        #   (type='assign', value='='),
        #   (type='string', value='user'),
        # Anything else is a parse error
        error_msg = f"Invalid syntax for chat attribute, got '{gathered}', expected role=\"value\""
        try:
            attr_name, attr_assign, attr_value = gathered  # pylint: disable=unbalanced-tuple-unpacking
        except ValueError:
            raise TemplateSyntaxError(error_msg, lineno) from None

        # Validate tag attributes
        if attr_name.value != "role" or attr_assign.value != "=":
            raise TemplateSyntaxError(error_msg, lineno)

        if attr_value.value not in SUPPORTED_TYPES:
            types = ",".join(SUPPORTED_TYPES)
            msg = f"Unknown role type '{attr_value}', use one of ({types})"
            raise TemplateSyntaxError(msg, lineno)

        # Pass the role name to the CallBlock node
        args: list[nodes.Expr] = [nodes.Const(attr_value.value)]

        # Message body
        body = parser.parse_statements(("name:endchat",), drop_needle=True)

        # Build messages list
        return nodes.CallBlock(self.call_method("_store_chat_messages", args), [], [], body).set_lineno(lineno)

    def _store_chat_messages(self, role, caller):
        """
        Helper callback.
        """
        parser = _ContentBlockParser()
        parser.feed(caller())
        cm = ChatMessage(role=role, content=parser.content)
        return cm.model_dump_json()