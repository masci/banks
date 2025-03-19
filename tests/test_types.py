import base64
from pathlib import Path

import pytest

from banks.types import ImageUrl, InputAudio


def test_image_url_from_base64():
    """Test creating ImageUrl from base64 encoded data"""
    test_data = "Hello, World!"
    base64_data = base64.b64encode(test_data.encode()).decode("utf-8")
    media_type = "image/jpeg"

    image_url = ImageUrl.from_base64(media_type, base64_data)
    expected_url = f"data:{media_type};base64,{base64_data}"
    assert image_url.url == expected_url


def test_image_url_from_path(tmp_path):
    """Test creating ImageUrl from a file path"""
    # Create a temporary test image file
    test_image = tmp_path / "test_image.jpg"
    test_content = b"fake image content"
    test_image.write_bytes(test_content)

    image_url = ImageUrl.from_path(test_image)

    # Verify the URL starts with the expected data URI prefix
    assert image_url.url.startswith("data:image/jpeg;base64,")

    # Decode the base64 part and verify the content matches
    base64_part = image_url.url.split(",")[1]
    decoded_content = base64.b64decode(base64_part)
    assert decoded_content == test_content


def test_image_url_from_path_nonexistent():
    """Test creating ImageUrl from a nonexistent file path"""
    with pytest.raises(FileNotFoundError):
        ImageUrl.from_path(Path("nonexistent.jpg"))


def test_input_audio_from_path(tmp_path):
    """Test creating InputAudio from a file path"""
    # Create a temporary test image file
    test_audio = tmp_path / "test_audio.wav"
    test_content = b"fake audio data"
    test_audio.write_bytes(test_content)

    input_audio = InputAudio.from_path(test_audio)

    assert input_audio.format == "wav"
    decoded_content = base64.b64decode(input_audio.data)
    assert decoded_content == test_content


def test_input_audio_from_path_nonexistent():
    """Test creating ImageUrl from a nonexistent file path"""
    with pytest.raises(FileNotFoundError):
        InputAudio.from_path(Path("nonexistent.wav"))
