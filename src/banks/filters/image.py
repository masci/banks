# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urlparse

from jinja2 import pass_context

from banks.types import CONTENT_BLOCK_END, ContentBlock, ImageUrl, content_block_start
from banks.utils import sentinel_from_context

BASE64_PATH_REGEX = re.compile(r"image\/.*;base64,.*")


def _is_url(string: str) -> bool:
    result = urlparse(string)
    if not result.scheme:
        return False

    if not result.netloc:
        # The only valid format when netloc is empty is base64 data urls
        return all([result.scheme == "data", BASE64_PATH_REGEX.match(result.path)])

    return True


@pass_context
def image(context, value: str | bytes) -> str:
    """Wrap the filtered value into a ContentBlock of type image.

    The resulting ChatMessage will have the field `content` populated with a list of ContentBlock objects.

    Example:
        ```jinja
        Describe what you see

        {{ "path/to/image/file" | image }}
        ```

    Important:
        this filter marks the content to cache by surrounding it with content block markers,
        so it's only useful when used within a `{% chat %}` block.
    """
    if isinstance(value, bytes):
        image_url = ImageUrl.from_bytes(bytes_str=value)
    elif _is_url(value):
        image_url = ImageUrl(url=value)
    else:
        image_url = ImageUrl.from_path(Path(value))

    block = ContentBlock.model_validate({"type": "image_url", "image_url": image_url})
    return f"{content_block_start(sentinel_from_context(context))}{block.model_dump_json()}{CONTENT_BLOCK_END}"
