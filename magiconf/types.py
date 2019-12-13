from magiconf.errors import ConfigError


def _unquote(val: str) -> str:
    while len(val) >= 2 and val[0] == val[-1] == '"':
        val = val[1:-1]

    return val


def boolean(val: str) -> bool:
    if val == "":
        return True

    if val in ("true", "True", "1"):
        return True

    if val in ("false", "False", "0"):
        return False

    raise ConfigError(f"{val} is not a boolean value")


def integer(val: str) -> int:
    # Strip out quotes so that quoted negative integers are parsed properly
    # (quoting is required due to argument parser treating unquoted words with
    # "minus" sign as flags)
    base = 10
    val = _unquote(val)
    unsigned_val = val.lower().lstrip("-+")
    if unsigned_val.startswith("0b"):
        base = 2
    elif unsigned_val.startswith("0o"):
        base = 8
    elif unsigned_val.startswith("0x"):
        base = 16

    try:
        return int(val, base)
    except ValueError:
        raise ConfigError(f"{val} is not an integer value")


def string(val: str) -> str:
    # Strip out pair end quotes so e.g. -foo="bar baz" resulting in
    # \"bar baz \" would return without quotes which is more natural
    return _unquote(val)


type_parsers = {
    int: integer,
    str: string,
    bool: boolean,
}
