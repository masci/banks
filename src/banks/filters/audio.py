# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
from pathlib import Path

from banks.types import ContentBlock, InputAudio


def audio(value: str) -> str:
    """Wrap the filtered value into a ContentBlock of type audio.

    The resulting ChatMessage will have the field `content` populated with a list of ContentBlock objects.

    Example:
        ```jinja
        Describe what you see

        {{ "path/to/audio/file" | audio }}
        ```
    """
    input_audio = InputAudio.from_path(Path(value))
    block = ContentBlock.model_validate({"type": "audio", "input_audio": input_audio})
    return f"<content_block>{block.model_dump_json()}</content_block>"
