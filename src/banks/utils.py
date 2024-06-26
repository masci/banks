import secrets


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
