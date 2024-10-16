# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
from enum import Enum
from inspect import Parameter, getdoc, signature
from typing import Callable

from pydantic import BaseModel
from typing_extensions import Self

from .utils import parse_params_from_docstring, python_type_to_jsonschema

# pylint: disable=invalid-name


class ContentBlockType(str, Enum):
    text = "text"
    image = "image"


class MediaTypeBlockType(str, Enum):
    image_jpeg = "image/jpeg"
    image_png = "image/png"
    image_gif = "image/gif"
    image_webp = "image/webp"


class CacheControl(BaseModel):
    type: str = "ephemeral"


class Source(BaseModel):
    type: str = "base64"
    media_type: MediaTypeBlockType
    data: str

    class Config:
        use_enum_values = True


class ContentBlock(BaseModel):
    type: ContentBlockType
    cache_control: CacheControl | None = None
    text: str | None = None
    source: Source | None = None

    class Config:
        use_enum_values = True


ChatMessageContent = list[ContentBlock] | str


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
