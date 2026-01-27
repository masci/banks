import json
from base64 import b64encode
from pathlib import Path

import pytest

from banks import Prompt
from banks.filters.document import _get_document_format_from_bytes, _get_document_format_from_url, _is_url, document


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

    # All text types are treated as txt
    assert content_block["type"] == "document"
    assert content_block["input_document"]["data"] == url
    assert content_block["input_document"]["format"] == "txt"


def test_is_url_variants():
    assert _is_url("relative/path.pdf") is False
    assert _is_url("https://example.com/document.pdf") is True
    assert _is_url("data:application/pdf;base64,AAAA") is True
    assert _is_url("data:text/plain;base64,AAAA") is True
    assert _is_url("data:audio/mp3;base64,AAAA") is False


def test_get_document_format_from_url():
    with pytest.raises(ValueError):
        _get_document_format_from_url("https://example.com/document.WAV")
    assert _get_document_format_from_url("https://example.com/document") == "pdf"


def test_get_document_from_bytes(tiny_pdf):
    # PDF file header bytes
    with open(tiny_pdf, "rb") as f:
        pdf_bytes = f.read()
    result = document(pdf_bytes)

    assert result.startswith("<content_block>")
    assert result.endswith("</content_block>")

    json_content = result[15:-16]  # Remove wrapper tags
    content_block = json.loads(json_content)

    assert content_block["type"] == "document"
    assert content_block["input_document"]["format"] == "pdf"
    assert content_block["input_document"]["data"] == b64encode(pdf_bytes).decode()


def test_get_document_from_b64_bytes():
    html_str = "<html><body><h1>Test Document</h1></body></html>"
    html_bytes = html_str.encode("utf-8")
    html_b64 = b64encode(html_bytes)
    result = document(html_b64)

    assert result.startswith("<content_block>")
    assert result.endswith("</content_block>")

    json_content = result[15:-16]  # Remove wrapper tags
    content_block = json.loads(json_content)

    # All non pdf documents are treated as txt
    assert content_block["type"] == "document"
    assert content_block["input_document"]["format"] == "txt"
    assert content_block["input_document"]["data"] == html_b64.decode()


def test_get_document_format_from_bytes(tiny_pdf):
    with open(tiny_pdf, "rb") as f:
        pdf_bytes = f.read()
    html_bytes = b"<html><body><h1>Test</h1></body></html>"
    xhtml_bytes = (
        b"<!DOCTYPE html>"
        b'<html xmlns="http://www.w3.org/1999/xhtml"><head><title>Test</title></head><body></body>'
        b"</html>"
    )
    css_bytes = (
        b"body {\n  margin: 0;\n  font-family: Arial, sans-serif;\n  background: #fff;\n  color: #222;\n}\n\n"
        b".btn {\n  display: inline-block;\n  padding: 8px 12px;\n  background: #007bff;\n  color: #fff;\n  border-radius: 4px;\n  text-decoration: none;\n}\n\n"
        b".btn:hover {\n  background: #0056b3;\n}"
    )
    txt_bytes = b"This is a plain text document.\nIt has multiple lines.\nEnd of document."
    md_bytes = (
        b"# This is a Markdown document\n\n"
        b"This document contains **bold** text and *italic* text."
        b"\n\n"
        b"- Item 1\n"
        b"- Item 2\n"
        b"- Item 3\n"
    )
    rst_bytes = (
        b"This is a reStructuredText document.\n"
        b"===============================\n\n"
        b"This document contains **bold** text and *italic* text.\n\n"
        b"- Item 1\n"
        b"- Item 2\n"
        b"- Item 3\n"
    )
    xml_bytes = b'<?xml version="1.0" encoding="UTF-8"?><note><to>User</to><from>Tester</from><heading>Reminder</heading><body>This is a test XML document.</body></note>'
    csv = b"Name,Age,Location\nAlice,30,New York\nBob,25,Los Angeles\nCharlie,35,Chicago\n"
    rtf = b"{\\rtf1\\ansi\\deff0 {\\fonttbl {\\f0 Arial;}}\\f0\\fs24 This is a simple RTF document.}"
    js = b"function greet(name) { console.log('Hello, ' + name + '!'); } greet('World');"
    mjs = b"export function add(a, b) { return a + b; } console.log(add(2, 3));"
    cjs = b"const fs = require('fs'); fs.readFile('example.txt', 'utf8', (err, data) => { if (err) throw err; console.log(data); });"
    json_bytes = b'{ "name": "John", "age": 30, "city": "New York" }'

    assert _get_document_format_from_bytes(pdf_bytes) == "pdf"
    assert _get_document_format_from_bytes(html_bytes) == "txt"
    assert _get_document_format_from_bytes(xhtml_bytes) == "txt"
    assert _get_document_format_from_bytes(css_bytes) == "txt"
    assert _get_document_format_from_bytes(txt_bytes) == "txt"
    assert _get_document_format_from_bytes(md_bytes) == "txt"
    assert _get_document_format_from_bytes(rst_bytes) == "txt"
    assert _get_document_format_from_bytes(xml_bytes) == "txt"
    assert _get_document_format_from_bytes(csv) == "txt"
    assert _get_document_format_from_bytes(rtf) == "txt"
    assert _get_document_format_from_bytes(js) == "txt"
    assert _get_document_format_from_bytes(mjs) == "txt"
    assert _get_document_format_from_bytes(cjs) == "txt"
    assert _get_document_format_from_bytes(json_bytes) == "txt"


def test_document_no_chat_block(tiny_pdf):
    prompt = Prompt("{{ test }} and {{ another | document }}")
    messages = prompt.chat_messages({"test": "hello world", "another": str(tiny_pdf)})
    assert len(messages) == 1
    message = messages[0]
    assert len(message.content) == 2
    assert message.content[0].text == "hello world and"  # type: ignore
    assert message.content[1].type == "document"  # type:ignore
