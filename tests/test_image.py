import json
from base64 import b64encode
from pathlib import Path

import pytest

from banks import Prompt
from banks.filters.image import _is_url, image


def test_is_url():
    """Test the internal URL validation function"""
    assert _is_url("https://example.com/image.jpg") is True
    assert _is_url("http://example.com/image.jpg") is True
    assert _is_url("ftp://example.com/image.jpg") is True
    assert _is_url("not_a_url.jpg") is False
    assert _is_url("/path/to/image.jpg") is False
    assert _is_url("relative/path/image.jpg") is False
    assert _is_url("") is False
    assert _is_url("https:\\example.com/image.jpg") is False


def test_image_with_url(jinja_context, unwrap_content_block):
    """Test image filter with a URL input"""
    url = "https://example.com/image.jpg"
    result = image(jinja_context, url)

    content_block = json.loads(unwrap_content_block(result))

    assert content_block["type"] == "image_url"
    assert content_block["image_url"]["url"] == url


def test_image_with_file_path(tmp_path, monkeypatch, jinja_context, unwrap_content_block):
    """Test image filter with a file path input"""
    monkeypatch.chdir(tmp_path)
    test_image = Path("test_image.jpg")
    test_content = b"fake image content"
    test_image.write_bytes(test_content)

    result = image(jinja_context, str(test_image))

    content_block = json.loads(unwrap_content_block(result))

    assert content_block["type"] == "image_url"
    assert content_block["image_url"]["url"].startswith("data:image/jpeg;base64,")


def test_image_path_traversal_blocked(jinja_context):
    """Test that absolute paths and traversal sequences outside CWD are blocked"""
    with pytest.raises(ValueError, match="Access denied"):
        image(jinja_context, "/etc/hosts")
    with pytest.raises(ValueError, match="Access denied"):
        image(jinja_context, "../../../etc/hosts")


def test_image_base64(tmp_path, jinja_context, unwrap_content_block):
    """Test image filter with a binary input"""
    test_image = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAABMgA"
    result = image(jinja_context, test_image)

    content_block = json.loads(unwrap_content_block(result))

    assert content_block["type"] == "image_url"
    assert content_block["image_url"]["url"].startswith("data:image/png;base64,")


def test_image_with_nonexistent_file(jinja_context):
    """Test image filter with a nonexistent file path"""
    with pytest.raises(FileNotFoundError):
        image(jinja_context, "nonexistent/image.jpg")


def test_image_from_bytes(jinja_context, unwrap_content_block):
    """Test image filter with bytes input"""
    png_bytes = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00"
    result = image(jinja_context, png_bytes)

    content_block = json.loads(unwrap_content_block(result))

    assert content_block["type"] == "image_url"
    assert content_block["image_url"]["url"] == f"data:image/png;base64,{b64encode(png_bytes).decode('utf-8')}"


def test_image_from_b64_bytes(jinja_context, unwrap_content_block):
    webp_bytes = b"RIFF\x1a\x00\x00\x00WEBPVP8 "
    b64_bytes = b64encode(webp_bytes)
    result = image(jinja_context, b64_bytes)

    content_block = json.loads(unwrap_content_block(result))

    assert content_block["type"] == "image_url"
    assert content_block["image_url"]["url"] == f"data:image/webp;base64,{b64_bytes.decode('utf-8')}"


def test_image_content_block_structure(jinja_context, unwrap_content_block):
    """Test the structure of the generated content block"""
    url = "https://example.com/image.jpg"
    result = image(jinja_context, url)

    content_block = json.loads(unwrap_content_block(result))

    # Verify the content block has all expected fields
    assert set(content_block.keys()) >= {"type", "image_url"}
    assert content_block["type"] == "image_url"
    assert isinstance(content_block["image_url"], dict)
    assert "url" in content_block["image_url"]


def test_image_no_chat_block():
    here = Path(__file__).parent
    prompt = Prompt("{{ test }} and {{ another | image }}")
    messages = prompt.chat_messages({"test": "hello world", "another": str(here / "data" / "1x1.png")})
    assert len(messages) == 1
    message = messages[0]
    assert len(message.content) == 2
    assert message.content[0].text == "hello world and"
    assert message.content[1].type == "image_url"
