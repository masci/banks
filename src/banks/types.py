# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
from __future__ import annotations

import base64
import re
from enum import Enum
from inspect import Parameter, getdoc, signature
from pathlib import Path
from typing import Callable, Union

from pydantic import BaseModel
from typing_extensions import Self

from .utils import parse_params_from_docstring, python_type_to_jsonschema

# pylint: disable=invalid-name
CONTENT_BLOCK_REGEX = re.compile(r"<content_block>((?s:.)*)<\/content_block>")


class ContentBlockType(str, Enum):
    text = "text"
    image_url = "image_url"


class CacheControl(BaseModel):
    type: str = "ephemeral"


class ImageUrl(BaseModel):
    url: str

    @classmethod
    def from_base64(cls, media_type: str, base64_str: str) -> Self:
        return cls(url=f"data:{media_type};base64,{base64_str}")

    @classmethod
    def from_path(cls, file_path: Path) -> Self:
        with open(file_path, "rb") as image_file:
            return cls.from_base64("image/jpeg", base64.b64encode(image_file.read()).decode("utf-8"))


class ContentBlock(BaseModel):
    type: ContentBlockType
    cache_control: CacheControl | None = None
    text: str | None = None
    image_url: ImageUrl | None = None


ChatMessageContent = Union[list[ContentBlock], str]


class ChatMessage(BaseModel):
    role: str
    content: str | ChatMessageContent
    tool_call_id: str | None = None
    name: str | None = None


class FunctionParameter(BaseModel):
    type: str
    description: str


class FunctionParameters(BaseModel):
    type: str = "object"
    properties: dict[str, FunctionParameter]
    required: list[str]


class Function(BaseModel):
    name: str
    description: str
    parameters: FunctionParameters


class Tool(BaseModel):
    """A model representing a Tool to be used in function calling.

    This model should dump the following:
    ```
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                },
                "required": ["location"],
            },
        },
        "import_path": "module.get_current_weather",
    }
    ```
    """

    type: str = "function"
    function: Function
    import_path: str

    @classmethod
    def from_callable(cls, func: Callable) -> Self:
        sig = signature(func)

        # Try getting params descriptions from docstrings
        param_docs = parse_params_from_docstring(func.__doc__ or "")

        # If the docstring is missing, use the qualname space-separated hopefully
        # the LLM will get some more context than just using the function name.
        description = getdoc(func) or " ".join(func.__qualname__.split("."))
        properties = {}
        required = []
        for name, param in sig.parameters.items():
            p = FunctionParameter(
                description=param_docs.get(name, {}).get("description", ""),
                type=python_type_to_jsonschema(param.annotation),
            )
            properties[name] = p
            if param.default == Parameter.empty:
                required.append(name)

        return cls(
            function=Function(
                name=func.__name__,
                description=description,
                parameters=FunctionParameters(properties=properties, required=required),
            ),
            import_path=f"{func.__module__}.{func.__qualname__}",
        )


def chat_message_from_text(role: str, content: str) -> ChatMessage:
    """
    Helper callback.
    """
    content_blocks: list[ContentBlock] = []

    # Find all content block matches
    matches = CONTENT_BLOCK_REGEX.finditer(content)
    last_end = 0
    for match in matches:
        # If there's text before the match, add it as a text content block
        if match.start() > last_end:
            text = content[last_end : match.start()].strip()
            if text:
                content_blocks.append(ContentBlock(type=ContentBlockType.text, text=text))

        # Add the parsed content block
        content_blocks.append(ContentBlock.model_validate_json(match.group(1)))
        last_end = match.end()

    # Add any remaining text after the last match
    if last_end < len(content):
        text = content[last_end:].strip()
        if text:
            content_blocks.append(ContentBlock(type=ContentBlockType.text, text=text))

    # If no content blocks were found, treat entire content as text
    if not content_blocks:
        content_blocks.append(ContentBlock(type=ContentBlockType.text, text=content))

    final_content = content_blocks

    if len(content_blocks) == 1:
        block = content_blocks[0]
        if block.type == "text" and block.cache_control is None:
            final_content = block.text or ""

    return ChatMessage(role=role, content=final_content)
