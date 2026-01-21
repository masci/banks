import json
from pathlib import Path

import pytest

from banks import Prompt
from banks.filters.video import _get_video_format_from_url, _is_url, video


@pytest.fixture
def empty_mov():
    here = Path(__file__).parent
    return here / "data" / "empty.mov"


def test_video_with_file_path(empty_mov):
    """Test video filter with a file path input"""
    result = video(str(empty_mov))

    # Verify the content block wrapper
    assert result.startswith("<content_block>")
    assert result.endswith("</content_block>")

    # Parse the JSON content
    json_content = result[15:-16]  # Remove wrapper tags
    content_block = json.loads(json_content)

    assert content_block["type"] == "video"
    assert content_block["input_video"]["format"].startswith("mov")


def test_video_with_nonexistent_file():
    """Test video filter with a nonexistent file path"""
    with pytest.raises(FileNotFoundError):
        video("nonexistent/video.mov")


def test_video_with_url():
    """Test video filter with a URL input (no filesystem access)."""
    url = "https://example.com/video.webm"
    result = video(url)

    assert result.startswith("<content_block>")
    assert result.endswith("</content_block>")

    json_content = result[15:-16]  # Remove wrapper tags
    content_block = json.loads(json_content)

    assert content_block["type"] == "video"
    assert content_block["input_video"]["data"] == url
    assert content_block["input_video"]["format"] == "webm"


def test_is_url_variants():
    assert _is_url("relative/path.mov") is False
    assert _is_url("https://example.com/video.mov") is True
    assert _is_url("data:video/mov;base64,AAAA") is True
    assert _is_url("data:text/plain;base64,AAAA") is False


def test_get_video_format_from_url():
    assert _get_video_format_from_url("https://example.com/video.MOV") == "mov"
    assert _get_video_format_from_url("https://example.com/video") == "mp4"


def test_video_no_chat_block(empty_mov):
    prompt = Prompt("{{ test }} and {{ another | video }}")
    messages = prompt.chat_messages({"test": "hello world", "another": str(empty_mov)})
    assert len(messages) == 1
    message = messages[0]
    assert len(message.content) == 2
    assert message.content[0].text == "hello world and"  # type: ignore
    assert message.content[1].type == "video"  # type:ignore
