# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
from __future__ import annotations

import base64
import re
from base64 import b64decode, b64encode
from binascii import Error as BinasciiError
from enum import Enum
from inspect import Parameter, getdoc, signature
from pathlib import Path
from typing import Callable, Literal, Union, cast

import filetype  # type: ignore[import-untyped]
from pydantic import BaseModel
from typing_extensions import Self

from .utils import parse_params_from_docstring, python_type_to_jsonschema

# pylint: disable=invalid-name
CONTENT_BLOCK_REGEX = re.compile(r"(<content_block>\{.*?\}<\/content_block>)|([^<](?:(?!<content_block>)[\s\S])*)")


def resolve_binary(bytes_str: bytes, *, as_base64: bool = True) -> bytes:
    """
    Resolve binary data between base64 and raw bytes.

    Args:
        bytes_str: Bytes data
        as_base64: Whether to return base64 encoded bytes or raw bytes

    Returns:
        b64 encoded bytes if input is not base64 encoded, else returns input as is.
    """
    # check if bytes_str is base64 encoded
    try:
        # Check if raw_bytes is already base64 encoded.
        # b64decode() can succeed on random binary data, so we
        # pass verify=True to make sure it's not a false positive
        raw_bytes = base64.b64decode(bytes_str, validate=True)
        b64_bytes = bytes_str
    except BinasciiError:
        # b64decode failed, leave as is
        raw_bytes = bytes_str
        b64_bytes = b64encode(bytes_str)
    return b64_bytes if as_base64 else raw_bytes


class ContentBlockType(str, Enum):
    text = "text"
    image_url = "image_url"
    audio = "audio"
    video = "video"
    document = "document"


class CacheControl(BaseModel):
    type: str = "ephemeral"


class ImageUrl(BaseModel):
    url: str

    @staticmethod
    def _mimetype_from_bytes(raw_bytes: bytes) -> str:
        kind = filetype.guess(raw_bytes)
        if kind is not None:
            return kind.mime
        # Default to jpeg if format cannot be determined
        return "image/jpeg"

    @classmethod
    def from_base64(cls, media_type: str, base64_str: str) -> Self:
        return cls(url=f"data:{media_type};base64,{base64_str}")

    @classmethod
    def from_path(cls, file_path: Path) -> Self:
        with open(file_path, "rb") as image_file:
            raw_bytes = image_file.read()
            mimetype = cls._mimetype_from_bytes(raw_bytes)
            return cls.from_base64(mimetype, base64.b64encode(raw_bytes).decode("utf-8"))

    @classmethod
    def from_bytes(cls, bytes_str: bytes) -> Self:
        """Create ImageUrl from bytes
        Args:
            bytes_str: Bytes data
        Returns:
            ImageUrl instance with base64 encoded bytes as URL
        """
        b64_bytes = resolve_binary(bytes_str)
        mimetype = cls._mimetype_from_bytes(b64decode(b64_bytes))
        return cls.from_base64(mimetype, b64_bytes.decode("utf-8"))


AudioFormat = Literal["mp3", "wav", "m4a", "webm", "ogg", "flac"]
VideoFormat = Literal["mp4", "mpg", "mov", "avi", "flv", "webm", "wmv", "3gp", "3gpp"]
# Because Claude only supports pdf and text, and Gemini only supports a small subset of text formats,
# we can default to 'txt' for any text-based format that is not pdf. This allows the data to be sent to the llm
# in an acceptable format, but the LLM should still be able to understand the content: e.g., html, markdown,
# xml, etc.
# If detecting text types should become desirable, I recommend using something like Google magicka
DocumentFormat = Literal["pdf", "txt"]


class InputAudio(BaseModel):
    data: str
    format: AudioFormat

    @classmethod
    def from_path(cls, file_path: Path) -> Self:
        with open(file_path, "rb") as audio_file:
            encoded_str = base64.b64encode(audio_file.read()).decode("utf-8")
            file_format = cast(AudioFormat, file_path.suffix[1:])
            return cls(data=encoded_str, format=file_format)

    @classmethod
    def from_url(cls, url: str, audio_format: AudioFormat) -> Self:
        """Create InputAudio from a URL.

        Args:
            url: The URL to the audio file
            audio_format: The audio format

        Returns:
            InputAudio instance with the URL as data
        """
        return cls(data=url, format=audio_format)

    @classmethod
    def from_bytes(cls, bytes_str: bytes, audio_format: AudioFormat) -> Self:
        """Create InputAudio from bytes

        Args:
            bytes_str: Bytes data
            audio_format: The audio format

        Returns:
            InputAudio instance with base64 encoded bytes as data
        """
        b64_bytes = resolve_binary(bytes_str)
        encoded_str = b64_bytes.decode("utf-8")
        return cls(data=encoded_str, format=audio_format)


class InputVideo(BaseModel):
    data: str
    format: VideoFormat

    @classmethod
    def from_path(cls, file_path: Path) -> Self:
        with open(file_path, "rb") as video_file:
            encoded_str = base64.b64encode(video_file.read()).decode("utf-8")
            file_format = cast(VideoFormat, file_path.suffix[1:])
            return cls(data=encoded_str, format=file_format)

    @classmethod
    def from_url(cls, url: str, video_format: VideoFormat) -> Self:
        """Create InputVideo from a URL.

        Args:
            url: The URL to the audio file
            video_format: The audio format

        Returns:
            InputVideo instance with the URL as data
        """
        return cls(data=url, format=video_format)

    @classmethod
    def from_bytes(cls, bytes_str: bytes, video_format: VideoFormat) -> Self:
        """Create InputVideo from bytes

        Args:
            bytes_str: Bytes data
            video_format: The video format

        Returns:
            InputVideo instance with base64 encoded bytes as data
        """
        b64_bytes = resolve_binary(bytes_str)
        encoded_str = b64_bytes.decode("utf-8")
        return cls(data=encoded_str, format=video_format)


class InputDocument(BaseModel):
    data: str
    format: DocumentFormat

    @classmethod
    def from_path(cls, file_path: Path) -> Self:
        with open(file_path, "rb") as document_file:
            encoded_str = base64.b64encode(document_file.read()).decode("utf-8")
            file_format = cast(DocumentFormat, file_path.suffix[1:])
            return cls(data=encoded_str, format=file_format)

    @classmethod
    def from_url(cls, url: str, document_format: DocumentFormat) -> Self:
        """Create InputDocument from a URL.

        Args:
            url: The URL to the document file
            document_format: The document format

        Returns:
            InputDocument instance with the URL as data
        """
        return cls(data=url, format=document_format)

    @classmethod
    def from_bytes(cls, bytes_str: bytes, document_format: DocumentFormat) -> Self:
        """Create InputDocument from bytes

        Args:
            bytes_str: Bytes data
            document_format: The document format

        Returns:
            InputDocument instance with base64 encoded bytes as data
        """
        b64_bytes = resolve_binary(bytes_str)
        encoded_str = b64_bytes.decode("utf-8")
        return cls(data=encoded_str, format=document_format)


class ContentBlock(BaseModel):
    type: ContentBlockType
    cache_control: CacheControl | None = None
    text: str | None = None
    image_url: ImageUrl | None = None
    input_audio: InputAudio | None = None
    input_video: InputVideo | None = None
    input_document: InputDocument | None = None


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
