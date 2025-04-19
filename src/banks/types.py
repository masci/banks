# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
from __future__ import annotations

import base64
import re
from enum import Enum
from inspect import Parameter, getdoc, signature
from pathlib import Path
from typing import Callable, Literal, Union, cast

from pydantic import BaseModel
from typing_extensions import Self

from .utils import parse_params_from_docstring, python_type_to_jsonschema

# pylint: disable=invalid-name
CONTENT_BLOCK_REGEX = re.compile(r"(<content_block>\{.*?\}<\/content_block>)|([^<](?:(?!<content_block>)[\s\S])*)")


class ContentBlockType(str, Enum):
    text = "text"
    image_url = "image_url"
    audio = "audio"


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


AudioFormat = Literal["mp3", "wav", "m4a", "webm", "ogg", "flac"]


class InputAudio(BaseModel):
    data: str
    format: AudioFormat

    @classmethod
    def from_path(cls, file_path: Path) -> Self:
        with open(file_path, "rb") as audio_file:
            encoded_str = base64.b64encode(audio_file.read()).decode("utf-8")
            file_format = cast(AudioFormat, file_path.suffix[1:])
            return cls(data=encoded_str, format=file_format)


class ContentBlock(BaseModel):
    type: ContentBlockType
    cache_control: CacheControl | None = None
    text: str | None = None
    image_url: ImageUrl | None = None
    input_audio: InputAudio | None = None


ChatMessageContent = Union[list[ContentBlock], str]


class ChatMessage(BaseModel):
    role: str
    content: ChatMessageContent
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
    for match in matches:
        if match.group(1):
            # content block match
            content_block_json_str = (
                match.group(1).strip().removeprefix("<content_block>").removesuffix("</content_block>")
            )
            content_blocks.append(ContentBlock.model_validate_json(content_block_json_str))
        elif match.group(2):
            # plain-text match
            text = match.group(2).strip()
            if text:
                content_blocks.append(ContentBlock(type=ContentBlockType.text, text=text))

    # If no content blocks were found, treat entire content as text
    if not content_blocks:
        content_blocks.append(ContentBlock(type=ContentBlockType.text, text=content))

    final_content = content_blocks

    return ChatMessage(role=role, content=final_content)
