# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
from __future__ import annotations

import re
from pathlib import Path
from typing import cast
from urllib.parse import urlparse

import filetype  # type: ignore[import-untyped]
from jinja2 import pass_context

from banks.types import CONTENT_BLOCK_END, AudioFormat, ContentBlock, InputAudio, content_block_start, resolve_binary
from banks.utils import sentinel_from_context

BASE64_AUDIO_REGEX = re.compile(r"audio\/.*;base64,.*")


def _is_url(string: str) -> bool:
    """Check if a string is a URL."""
    result = urlparse(string)
    if not result.scheme:
        return False

    if not result.netloc:
        # The only valid format when netloc is empty is base64 data urls
        return all([result.scheme == "data", BASE64_AUDIO_REGEX.match(result.path)])

    return True


def _get_audio_format_from_url(url: str) -> AudioFormat:
    """Extract audio format from URL.

    Tries to determine format from URL path or defaults to mp3.
    """
    parsed = urlparse(url)
    path = parsed.path.lower()
    for fmt in ("mp3", "wav", "m4a", "webm", "ogg", "flac"):
        if path.endswith(f".{fmt}"):
            return cast(AudioFormat, fmt)
    # Default to mp3 if format cannot be determined
    return "mp3"


def _get_audio_format_from_bytes(data: bytes) -> AudioFormat:
    """Extract audio format from bytes data using filetype library."""
    kind = filetype.guess(data)
    if kind is not None:
        fmt = kind.extension
        if fmt in ("mp3", "wav", "m4a", "webm", "ogg", "flac"):
            return cast(AudioFormat, fmt)
    # Default to mp3 if format cannot be determined
    return "mp3"


@pass_context
def audio(context, value: str | bytes) -> str:
    """Wrap the filtered value into a ContentBlock of type audio.

    The resulting ChatMessage will have the field `content` populated with a list of ContentBlock objects.

    Supports both file paths and URLs (including data URLs).

    Example:
        ```jinja
        {{ "path/to/audio/file.mp3" | audio }}
        {{ "https://example.com/audio.mp3" | audio }}
        ```
    """
    if isinstance(value, bytes):
        audio_format = _get_audio_format_from_bytes(resolve_binary(value, as_base64=False))
        input_audio = InputAudio.from_bytes(value, audio_format=audio_format)
    elif _is_url(value):
        audio_format = _get_audio_format_from_url(value)
        input_audio = InputAudio.from_url(value, audio_format)
    else:
        input_audio = InputAudio.from_path(Path(value))
    block = ContentBlock.model_validate({"type": "audio", "input_audio": input_audio})
    return f"{content_block_start(sentinel_from_context(context))}{block.model_dump_json()}{CONTENT_BLOCK_END}"
