# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
import re
from pathlib import Path
from urllib.parse import urlparse

from banks.types import ContentBlock, ImageUrl

BASE64_PATH_REGEX = re.compile(r"image\/.*;base64,.*")


def _is_url(string: str) -> bool:
    result = urlparse(string)
    if not result.scheme:
        return False

    if not result.netloc:
        # The only valid format when netloc is empty is base64 data urls
        return all([result.scheme == "data", BASE64_PATH_REGEX.match(result.path)])

    return True


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
