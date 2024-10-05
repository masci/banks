# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
from enum import Enum

from pydantic import BaseModel

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
