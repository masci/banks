import pytest
import regex as re

from banks.utils import generate_canary_word, strtobool


def test_generate_canary_word_defaults():
    default = generate_canary_word()
    assert re.match(r"BANKS\[.{8}\]", default)


def test_generate_canary_word_params():
    only_token = generate_canary_word(prefix="", suffix="", token_length=16)
    assert re.match(r".{16}", only_token)

    only_prefix = generate_canary_word(prefix="foo", suffix="")
    assert re.match(r"foo.{8}", only_prefix)

    only_suffix = generate_canary_word(prefix="", suffix="foo")
    assert re.match(r".{8}foo", only_suffix)


def test_strtobool_error():
    with pytest.raises(ValueError):
        strtobool("42")


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("y", True),
        ("yes", True),
        ("t", True),
        ("true", True),
        ("on", True),
        ("1", True),
        ("n", False),
        ("no", False),
        ("f", False),
        ("false", False),
        ("off", False),
        ("0", False),
        pytest.param("42", True, marks=pytest.mark.xfail),
    ],
)
def test_strtobool(test_input, expected):
    assert strtobool(test_input) == expected
