import json
from pathlib import Path

import pytest

from banks import Prompt
from banks.filters.document import _get_document_format_from_url, _is_url, document


@pytest.fixture
def tiny_pdf():
    here = Path(__file__).parent
    return here / "data" / "1x1.pdf"


def test_document_with_file_path(tiny_pdf):
    """Test document filter with a file path input"""
    result = document(str(tiny_pdf))

    # Verify the content block wrapper
    assert result.startswith("<content_block>")
    assert result.endswith("</content_block>")

    # Parse the JSON content
    json_content = result[15:-16]  # Remove wrapper tags
    content_block = json.loads(json_content)

    assert content_block["type"] == "document"
    assert content_block["input_document"]["format"].startswith("pdf")


def test_document_with_nonexistent_file():
    """Test document filter with a nonexistent file path"""
    with pytest.raises(FileNotFoundError):
        document("nonexistent/document.pdf")


def test_document_with_url():
    """Test document filter with a URL input (no filesystem access)."""
    url = "https://example.com/document.css"
    result = document(url)

    assert result.startswith("<content_block>")
    assert result.endswith("</content_block>")

    json_content = result[15:-16]  # Remove wrapper tags
    content_block = json.loads(json_content)

    assert content_block["type"] == "document"
    assert content_block["input_document"]["data"] == url
    assert content_block["input_document"]["format"] == "css"


def test_is_url_variants():
    assert _is_url("relative/path.pdf") is False
    assert _is_url("https://example.com/document.pdf") is True
    assert _is_url("data:application/pdf;base64,AAAA") is True
    assert _is_url("data:text/plain;base64,AAAA") is True
    assert _is_url("data:audio/mp3;base64,AAAA") is False


def test_get_document_format_from_url():
    assert _get_document_format_from_url("https://example.com/document.WAV") == "pdf"
    assert _get_document_format_from_url("https://example.com/document") == "pdf"


def test_document_no_chat_block(tiny_pdf):
    prompt = Prompt("{{ test }} and {{ another | document }}")
    messages = prompt.chat_messages({"test": "hello world", "another": str(tiny_pdf)})
    assert len(messages) == 1
    message = messages[0]
    assert len(message.content) == 2
    assert message.content[0].text == "hello world and"  # type: ignore
    assert message.content[1].type == "document"  # type:ignore
