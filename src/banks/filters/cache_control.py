# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
from banks.types import ContentBlock


def cache_control(value: str, cache_type: str = "ephemeral") -> str:
    """

    Example:
    ```
    {{ "This is a long, long text" | cache_control "ephemeral" }}

    This is short and won't be cached.
    ```

    """
    block = ContentBlock.model_validate({"type": "text", "text": value, "cache_control": {"type": cache_type}})
    return f"<content_block_txt>{block.model_dump_json()}</content_block_txt>"
