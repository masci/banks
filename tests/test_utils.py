import pytest
import regex as re

from banks.utils import generate_canary_word, parse_params_from_docstring, python_type_to_jsonschema, strtobool


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


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (type("I am a string"), "string"),  # noqa
        (type(42), "integer"),  # noqa
        (type(0.42), "number"),  # noqa
        (type(True), "boolean"),  # noqa
        (type([]), "array"),
        (type({"foo": "bar"}), "object"),
    ],
)
def test_python_type_to_jsonschema(test_input, expected):
    assert python_type_to_jsonschema(test_input) == expected
    with pytest.raises(ValueError, match="Unsupported type: <class 'type'>"):
        python_type_to_jsonschema(type(Exception))


def test_parse_params_from_docstring_google():
    def my_test_function(test_param: str):
        """A docstring.

        Args:
            test_param (str): The test parameter.
        """
        pass

    assert parse_params_from_docstring(my_test_function.__doc__) == {  # type: ignore
        "test_param": {"annotation": "str", "description": "The test parameter."}
    }


def test_parse_params_from_docstring_numpy():
    def my_test_function(test_param: str):
        """A docstring.

        Parameters
        ----------
        test_param : str
            The test parameter.
        """
        pass

    assert parse_params_from_docstring(my_test_function.__doc__) == {  # type: ignore
        "test_param": {"annotation": "str", "description": "The test parameter."}
    }


def test_parse_params_from_docstring_sphinx():
    def my_test_function(test_param: str):
        """A docstring.

        :param test_param: The test parameter.
        :type test_param: str
        """
        pass

    assert parse_params_from_docstring(my_test_function.__doc__) == {  # type: ignore
        "test_param": {"annotation": "str", "description": "The test parameter."}
    }


def test_parse_params_from_docstring_empty():
    assert parse_params_from_docstring("") == {}
