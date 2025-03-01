# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
import re

from jinja2 import TemplateSyntaxError, nodes
from jinja2.ext import Extension

from banks.types import ChatMessage, ContentBlock, ContentBlockType

SUPPORTED_TYPES = ("system", "user", "assistant")
CONTENT_BLOCK_REGEX = re.compile(r"<content_block>((?s:.)*)<\/content_block>")


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
        content_blocks: list[ContentBlock] = []
        block_content = caller()

        # Find all content block matches
        matches = CONTENT_BLOCK_REGEX.finditer(block_content)
        last_end = 0
        for match in matches:
            # If there's text before the match, add it as a text content block
            if match.start() > last_end:
                text = block_content[last_end : match.start()].strip()
                if text:
                    content_blocks.append(ContentBlock(type=ContentBlockType.text, text=text))

            # Add the parsed content block
            content_blocks.append(ContentBlock.model_validate_json(match.group(1)))
            last_end = match.end()

        # Add any remaining text after the last match
        if last_end < len(block_content):
            text = block_content[last_end:].strip()
            if text:
                content_blocks.append(ContentBlock(type=ContentBlockType.text, text=text))

        # If no content blocks were found, treat entire content as text
        if not content_blocks:
            content_blocks.append(ContentBlock(type=ContentBlockType.text, text=block_content))

        content = content_blocks

        if len(content_blocks) == 1:
            block = content_blocks[0]
            if block.type == "text" and block.cache_control is None:
                content = block.text or ""

        cm = ChatMessage(role=role, content=content)
        return cm.model_dump_json(exclude_none=True) + "\n"
