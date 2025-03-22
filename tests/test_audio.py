import json
from pathlib import Path

import pytest

from banks import Prompt
from banks.filters.audio import audio


@pytest.fixture
def empty_wav():
    here = Path(__file__).parent
    return here / "data" / "empty.wav"


def test_audio_with_file_path(empty_wav):
    """Test audio filter with a file path input"""
    result = audio(str(empty_wav))

    # Verify the content block wrapper
    assert result.startswith("<content_block>")
    assert result.endswith("</content_block>")

    # Parse the JSON content
    json_content = result[15:-16]  # Remove wrapper tags
    content_block = json.loads(json_content)

    assert content_block["type"] == "audio"
    assert content_block["input_audio"]["format"].startswith("wav")


def test_audio_with_nonexistent_file():
    """Test audio filter with a nonexistent file path"""
    with pytest.raises(FileNotFoundError):
        audio("nonexistent/audio.wav")


def test_audio_no_chat_block(empty_wav):
    prompt = Prompt("{{ test }} and {{ another | audio }}")
    messages = prompt.chat_messages({"test": "hello world", "another": str(empty_wav)})
    assert len(messages) == 1
    message = messages[0]
    assert len(message.content) == 2
    assert message.content[0].text == "hello world and"  # type: ignore
    assert message.content[1].type == "audio"  # type:ignore
