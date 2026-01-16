# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
import re
from pathlib import Path
from typing import cast
from urllib.parse import urlparse

from banks.types import ContentBlock, DocumentFormat, InputDocument

BASE64_DOCUMENT_REGEX = re.compile(r"(text|application)\/.*;base64,.*")


def _is_url(string: str) -> bool:
    """Check if a string is a URL."""
    result = urlparse(string)
    if not result.scheme:
        return False

    if not result.netloc:
        # The only valid format when netloc is empty is base64 data urls
        return all([result.scheme == "data", BASE64_DOCUMENT_REGEX.match(result.path)])

    return True


def _get_document_format_from_url(url: str) -> DocumentFormat:
    """Extract document format from URL.

    Tries to determine format from URL path or defaults to pdf.
    """
    parsed = urlparse(url)
    path = parsed.path.lower()
    # Gemini supported file types https://ai.google.dev/gemini-api/docs/file-input-methods
    # text/html
    # text/css
    # text/plain
    # text/xml
    # text/scv
    # text/rtf
    # text/javascript
    # application/json
    # application/pdf

    # Claude supported file types
    # application/pdf
    # text/plain

    # OpenAI supported file types
    # application/pdf

    for fmt in (
        "pdf",
        "html",
        "htm",
        "xhtml",
        "css",
        "txt",
        "md",
        "markdown",
        "rst",
        "xml",
        "csv",
        "rtf",
        "js",
        "mjs",
        "cjs",
        "javascript",
        "json",
    ):
        if path.endswith(f".{fmt}"):
            return cast(DocumentFormat, fmt)
    # Default to pdf if format cannot be determined
    return "pdf"


def document(value: str) -> str:
    """Wrap the filtered value into a ContentBlock of type document.

    The resulting ChatMessage will have the field `content` populated with a list of ContentBlock objects.

    Supports both file paths and URLs (including data URLs).

    Example:
        ```jinja
        {{ "path/to/document/file.pdf" | document }}
        {{ "https://example.com/document.pdf" | document }}
        ```
    """
    if _is_url(value):
        document_format = _get_document_format_from_url(value)
        input_document = InputDocument.from_url(value, document_format)
    else:
        input_document = InputDocument.from_path(Path(value))
    block = ContentBlock.model_validate({"type": "document", "input_document": input_document})
    return f"<content_block>{block.model_dump_json()}</content_block>"
