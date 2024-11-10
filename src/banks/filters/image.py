# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
from pathlib import Path
from urllib.parse import urlparse

from banks.types import ContentBlock, ImageUrl


def _is_url(string: str) -> bool:
    result = urlparse(string)
    return all([result.scheme, result.netloc])


def image(value: str) -> str:
    """Wrap the filtered value into a ContentBlock of type image.

    The resulting ChatMessage will have the field `content` populated with a list of ContentBlock objects.

    Example:
        ```jinja
        Describe what you see

        {{ "path/to/image/file" | image }}
        ```

    Important:
        this filter marks the content to cache by surrounding it with `<content_block>` and
        `</content_block>`, so it's only useful when used within a `{% chat %}` block.
    """
    if _is_url(value):
        image_url = ImageUrl(url=value)
    else:
        image_url = ImageUrl.from_path(Path(value))

    block = ContentBlock.model_validate({"type": "image_url", "image_url": image_url})
    return f"<content_block>{block.model_dump_json()}</content_block>"
