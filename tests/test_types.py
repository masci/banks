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


def test_image_url_from_path(tmp_path, monkeypatch):
    """Test creating ImageUrl from a file path"""
    monkeypatch.chdir(tmp_path)
    test_image = Path("test_image.jpg")
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


def test_image_url_from_path_outside_cwd():
    """Test that paths outside CWD are rejected"""
    with pytest.raises(ValueError, match="Access denied"):
        ImageUrl.from_path(Path("/etc/hosts"))


def test_image_url_from_path_with_media_root(tmp_path, monkeypatch):
    """Test that BANKS_MEDIA_ROOT is used when set"""
    monkeypatch.setenv("BANKS_MEDIA_ROOT", str(tmp_path))
    test_image = tmp_path / "test_image.jpg"
    test_image.write_bytes(b"fake image content")

    image_url = ImageUrl.from_path(test_image)
    assert image_url.url.startswith("data:image/jpeg;base64,")


def test_image_url_from_path_outside_media_root(tmp_path, monkeypatch):
    """Test that paths outside BANKS_MEDIA_ROOT are rejected"""
    monkeypatch.setenv("BANKS_MEDIA_ROOT", str(tmp_path))
    with pytest.raises(ValueError, match="Access denied"):
        ImageUrl.from_path(Path("/etc/hosts"))


def test_input_audio_from_path(tmp_path, monkeypatch):
    """Test creating InputAudio from a file path"""
    monkeypatch.chdir(tmp_path)
    test_audio = Path("test_audio.wav")
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


def test_input_audio_from_path_outside_cwd():
    """Test that paths outside CWD are rejected"""
    with pytest.raises(ValueError, match="Access denied"):
        InputAudio.from_path(Path("/etc/hosts"))
