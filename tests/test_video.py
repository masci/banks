import json
from base64 import b64encode
from pathlib import Path

import pytest

from banks import Prompt
from banks.filters.video import _get_video_format_from_bytes, _get_video_format_from_url, _is_url, video


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


def test_get_video_from_bytes():
    mp4_bytes = b"\x00\x00\x00\x18ftypmp42"
    result = video(mp4_bytes)

    assert result.startswith("<content_block>")
    assert result.endswith("</content_block>")

    json_content = result[15:-16]  # Remove wrapper tags
    content_block = json.loads(json_content)

    assert content_block["type"] == "video"
    assert content_block["input_video"]["format"] == "mp4"
    assert content_block["input_video"]["data"] == b64encode(mp4_bytes).decode("utf-8")


def test_get_video_from_b64_bytes():
    webm_bytes = b"\x1a\x45\xdf\xa3\x42\x82\x84webm"
    result = video(webm_bytes)

    assert result.startswith("<content_block>")
    assert result.endswith("</content_block>")

    json_content = result[15:-16]  # Remove wrapper tags
    content_block = json.loads(json_content)

    assert content_block["type"] == "video"
    assert content_block["input_video"]["format"] == "webm"
    assert content_block["input_video"]["data"] == b64encode(webm_bytes).decode("utf-8")


def test_get_video_format_from_bytes():
    mp4 = b"\x00\x00\x00\x18ftypmp42" + b"\x00" * (0x18 - len(b"\x00\x00\x00\x18ftypmp42"))
    mpeg = b"\x00\x00\x01\xba"
    mov = b"\x00\x00\x00\x14ftypqt  " + b"\x00" * (0x14 - len(b"\x00\x00\x00\x14ftypqt  "))
    avi = b"RIFF$\x00\x00\x00AVI LIST"
    flv = b"FLV\x01\x05\x00\x00\x00\x09"
    webm = b"\x1a\x45\xdf\xa3\x42\x82\x84webm"
    wmv = bytes.fromhex("3026B2758E66CF11A6D900AA0062CE6C")
    gpp = b"\x00\x00\x00\x18ftyp3gp5\x00\x00\x00\x00isom3gp4"
    unknown = b"\x00\x01\x02\x03\x04\x05"

    assert _get_video_format_from_bytes(mp4) == "mp4"
    assert _get_video_format_from_bytes(mpeg) == "mpg"
    assert _get_video_format_from_bytes(mov) == "mov"
    assert _get_video_format_from_bytes(avi) == "avi"
    assert _get_video_format_from_bytes(flv) == "flv"
    assert _get_video_format_from_bytes(webm) == "webm"
    assert _get_video_format_from_bytes(wmv) == "wmv"
    assert _get_video_format_from_bytes(gpp) == "3gp"
    assert _get_video_format_from_bytes(unknown) == "mp4"  # Default


def test_video_no_chat_block(empty_mov):
    prompt = Prompt("{{ test }} and {{ another | video }}")
    messages = prompt.chat_messages({"test": "hello world", "another": str(empty_mov)})
    assert len(messages) == 1
    message = messages[0]
    assert len(message.content) == 2
    assert message.content[0].text == "hello world and"  # type: ignore
    assert message.content[1].type == "video"  # type:ignore
