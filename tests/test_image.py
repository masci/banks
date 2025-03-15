import json
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


def test_image_with_url():
    """Test image filter with a URL input"""
    url = "https://example.com/image.jpg"
    result = image(url)

    # Verify the content block wrapper
    assert result.startswith("<content_block>")
    assert result.endswith("</content_block>")

    # Parse the JSON content
    json_content = result[15:-16]  # Remove wrapper tags
    content_block = json.loads(json_content)

    assert content_block["type"] == "image_url"
    assert content_block["image_url"]["url"] == url


def test_image_with_file_path(tmp_path):
    """Test image filter with a file path input"""
    # Create a temporary test image file
    test_image = tmp_path / "test_image.jpg"
    test_content = b"fake image content"
    test_image.write_bytes(test_content)

    result = image(str(test_image))

    # Verify the content block wrapper
    assert result.startswith("<content_block>")
    assert result.endswith("</content_block>")

    # Parse the JSON content
    json_content = result[15:-16]  # Remove wrapper tags
    content_block = json.loads(json_content)

    assert content_block["type"] == "image_url"
    assert content_block["image_url"]["url"].startswith("data:image/jpeg;base64,")


def test_image_with_nonexistent_file():
    """Test image filter with a nonexistent file path"""
    with pytest.raises(FileNotFoundError):
        image("nonexistent/image.jpg")


def test_image_content_block_structure():
    """Test the structure of the generated content block"""
    url = "https://example.com/image.jpg"
    result = image(url)

    json_content = result[15:-16]  # Remove wrapper tags
    content_block = json.loads(json_content)

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
