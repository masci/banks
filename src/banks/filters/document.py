# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
from __future__ import annotations

import mimetypes
import re
from pathlib import Path
from typing import cast
from urllib.parse import urlparse

import filetype  # type: ignore[import-untyped]

from banks.types import ContentBlock, DocumentFormat, InputDocument, resolve_binary

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
    # text/csv
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
        # Because Claude only supports pdf and text, and Gemini only supports a small subset of text formats,
        # we can default to 'txt' for any text-based format that is not pdf. This allows the data to be sent to the llm
        # in an acceptable format, but the LLM should still be able to understand the content: e.g., html, markdown,
        # xml, etc.
        if path.endswith(f".{fmt}"):
            if fmt == "pdf":
                return cast(DocumentFormat, "pdf")
            return "txt"
    mime = mimetypes.guess_type(path)[0]
    if mime is not None and mime.startswith("text/"):
        return "txt"
    # With urls, the likelihood seems sufficiently high that it's probably a pdf if not otherwise indicated
    if mime is None:
        return "pdf"
    # Document type indicated to be other than pdf or text type
    raise ValueError("Unsupported document format: " + path)


def _get_document_format_from_bytes(data: bytes) -> DocumentFormat:
    """Extract document format from bytes data using filetype library."""
    # First check for pdf (only non text based format) and RTF formats (can be detected by file header)
    kind = filetype.guess(data)
    if kind is not None:
        fmt = kind.extension
        if fmt == "pdf":
            return cast(DocumentFormat, fmt)

    # filetype is good at detecting binary formats, but not text-based ones.
    # So, this is a good indicator that it's text-based.
    # Because Claude only supports pdf and text, and Gemini only supports a small subset of text formats,
    # we can default to 'txt' for any text-based format that is not pdf. This allows the data to be sent to the llm in
    # an acceptable format, but the LLM should still be able to understand the content: e.g., html, markdown, xml, etc.
    # If detecting text types should become desirable, I recommend using something like Google magicka
    if kind is None or kind.extension == "rtf":
        return "txt"
    # There are many common document types (like word, excel, powerpoint, etc.) that are not supported.
    raise ValueError("Unsupported document format: " + kind.extension)


def document(value: str | bytes) -> str:
    """Wrap the filtered value into a ContentBlock of type document.

    The resulting ChatMessage will have the field `content` populated with a list of ContentBlock objects.

    Supports both file paths and URLs (including data URLs).

    Example:
        ```jinja
        {{ "path/to/document/file.pdf" | document }}
        {{ "https://example.com/document.pdf" | document }}
        ```
    """
    if isinstance(value, bytes):
        document_format = _get_document_format_from_bytes(resolve_binary(value, as_base64=False))
        input_document = InputDocument.from_bytes(value, document_format=document_format)
    elif _is_url(value):
        document_format = _get_document_format_from_url(value)
        input_document = InputDocument.from_url(value, document_format)
    else:
        input_document = InputDocument.from_path(Path(value))
    block = ContentBlock.model_validate({"type": "document", "input_document": input_document})
    return f"<content_block>{block.model_dump_json()}</content_block>"
