import secrets

from griffe import Docstring, parse_google, parse_numpy, parse_sphinx


def strtobool(val: str) -> bool:
    """
    Convert a string representation of truth to True or False.

    True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
    are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
    'val' is anything else.
    """
    val = val.lower()
    if val in ("y", "yes", "t", "true", "on", "1"):
        return True

    if val in ("n", "no", "f", "false", "off", "0"):
        return False

    msg = f"invalid truth value {val}"
    raise ValueError(msg)


def generate_canary_word(prefix: str = "BANKS[", suffix: str = "]", token_length: int = 8) -> str:
    return f"{prefix}{secrets.token_hex(token_length // 2)}{suffix}"


def python_type_to_jsonschema(python_type: type) -> str:
    """Given a Python type, returns the jsonschema string describing it."""
    if python_type is str:
        return "string"
    if python_type is int:
        return "integer"
    if python_type is float:
        return "number"
    if python_type is bool:
        return "boolean"
    if python_type is list:
        return "array"
    if python_type is dict:
        return "object"

    msg = f"Unsupported type: {python_type}"
    raise ValueError(msg)


def parse_params_from_docstring(docstring: str) -> dict[str, dict[str, str]]:
    param_docs = []
    ds = Docstring(docstring)
    for parser in (parse_google, parse_numpy, parse_sphinx):
        sections = parser(ds)
        for section in sections:
            if section.kind == "parameters":
                param_docs = section.value
                break
        if param_docs:
            break

    ret = {}
    for d in param_docs:
        d_dict = d.as_dict()
        ret[d_dict.pop("name")] = d_dict

    return ret
