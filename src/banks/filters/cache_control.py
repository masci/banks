# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
from jinja2 import pass_context

from banks.types import CONTENT_BLOCK_END, ContentBlock, content_block_start
from banks.utils import sentinel_from_context


@pass_context
def cache_control(context, value: str, cache_type: str = "ephemeral") -> str:
    """Wrap the filtered value into a ContentBlock with the proper cache_control field set.

    The resulting ChatMessage will have the field `content` populated with a list of ContentBlock objects.

    Example:
        ```jinja
        {{ "This is a long, long text" | cache_control("ephemeral") }}

        This is short and won't be cached.
        ```

    Important:
        this filter marks the content to cache by surrounding it with content block markers,
        so it's only useful when used within a `{% chat %}` block.
    """
    block = ContentBlock.model_validate({"type": "text", "text": value, "cache_control": {"type": cache_type}})
    return f"{content_block_start(sentinel_from_context(context))}{block.model_dump_json()}{CONTENT_BLOCK_END}"
