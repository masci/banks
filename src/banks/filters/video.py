# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
import re
from pathlib import Path
from typing import cast
from urllib.parse import urlparse

from banks.types import ContentBlock, InputVideo, VideoFormat

BASE64_VIDEO_REGEX = re.compile(r"video\/.*;base64,.*")


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


def video(value: str) -> str:
    """Wrap the filtered value into a ContentBlock of type video.

    The resulting ChatMessage will have the field `content` populated with a list of ContentBlock objects.

    Supports both file paths and URLs (including data URLs).

    Example:
        ```jinja
        {{ "path/to/video/file.mp4" | video }}
        {{ "https://example.com/video.mp4" | video }}
        ```
    """
    if _is_url(value):
        video_format = _get_video_format_from_url(value)
        input_video = InputVideo.from_url(value, video_format)
    else:
        input_video = InputVideo.from_path(Path(value))
    block = ContentBlock.model_validate({"type": "video", "input_video": input_video})
    return f"<content_block>{block.model_dump_json()}</content_block>"
