# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
from __future__ import annotations

import re
from pathlib import Path
from typing import cast
from urllib.parse import urlparse

import filetype  # type: ignore[import-untyped]
from filetype.types.video import IsoBmff  # type: ignore[import-untyped]

from banks.types import ContentBlock, InputVideo, VideoFormat, resolve_binary

BASE64_VIDEO_REGEX = re.compile(r"video\/.*;base64,.*")


class M3gp(IsoBmff):
    """
    Implements the 3gp video type matcher.

    The type matcher in the filetype lib does not work correctly for 3gp files,
    so implement our own here.
    """

    MIME = "video/3gpp"
    EXTENSION = "3gp"

    def __init__(self):
        super().__init__(mime=M3gp.MIME, extension=M3gp.EXTENSION)

    def match(self, buf):
        if not self._is_isobmff(buf):
            return False

        major_brand, _, compatible_brands = self._get_ftyp(buf)
        for brand in compatible_brands:
            if brand in ["3gp4", "3gp5", "3gpp"]:
                return True
        return major_brand in ["3gp4", "3gp5", "3gpp"]


def _is_url(string: str) -> bool:
    """Check if a string is a URL."""
    result = urlparse(string)
    if not result.scheme:
        return False

    if not result.netloc:
        # The only valid format when netloc is empty is base64 data urls
        return all([result.scheme == "data", BASE64_VIDEO_REGEX.match(result.path)])

    return True


def _get_video_format_from_url(url: str) -> VideoFormat:
    """Extract video format from URL.

    Tries to determine format from URL path or defaults to mp4.
    """
    parsed = urlparse(url)
    path = parsed.path.lower()

    # Based on formats supported by Gemini https://ai.google.dev/gemini-api/docs/video-understanding
    for fmt in ("mp4", "mpeg", "mov", "avi", "flv", "mpg", "webm", "wmv", "3gpp"):
        if path.endswith(f".{fmt}"):
            return cast(VideoFormat, fmt)
    # Default to mp4 if format cannot be determined
    return "mp4"


def _get_video_format_from_bytes(data: bytes) -> VideoFormat:
    """Extract video format from bytes data using filetype library."""
    m3gp = M3gp()
    if m3gp not in filetype.types:
        filetype.add_type(m3gp)

    kind = filetype.guess(data)
    if kind is not None:
        fmt = kind.extension
        if fmt in ("mp4", "mpg", "mov", "avi", "flv", "webm", "wmv", "3gp"):
            return cast(VideoFormat, fmt)
    # Default to mp4 if format cannot be determined
    return "mp4"


def video(value: str | bytes) -> str:
    """Wrap the filtered value into a ContentBlock of type video.

    The resulting ChatMessage will have the field `content` populated with a list of ContentBlock objects.

    Supports both file paths and URLs (including data URLs).

    Example:
        ```jinja
        {{ "path/to/video/file.mp4" | video }}
        {{ "https://example.com/video.mp4" | video }}
        ```
    """
    if isinstance(value, bytes):
        video_format = _get_video_format_from_bytes(resolve_binary(value, as_base64=False))
        input_video = InputVideo.from_bytes(value, video_format=video_format)
    elif _is_url(value):
        video_format = _get_video_format_from_url(value)
        input_video = InputVideo.from_url(value, video_format)
    else:
        input_video = InputVideo.from_path(Path(value))
    block = ContentBlock.model_validate({"type": "video", "input_video": input_video})
    return f"<content_block>{block.model_dump_json()}</content_block>"
