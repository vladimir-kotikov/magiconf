from argparse import ArgumentParser
from dataclasses import Field
from typing import Dict, Iterable, Optional

from magiconf.errors import ConfigError


def _unquote(val: str) -> str:
    while len(val) >= 2 and val[0] == val[-1] == '"':
        val = val[1:-1]

    return val


def boolean(val: Optional[str]) -> bool:
    if val is None or val == "":
        return True

    if val in ("true", "True"):
        return True

    if val in ("false", "False"):
        return False

    raise ConfigError(f"{val} is not a boolean value")


def integer(val: Optional[str]) -> Optional[int]:
    if val is None:
        return val

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
    except TypeError:
        raise ConfigError(f"{val} is not an integer value")


def string(val: Optional[str]) -> Optional[str]:
    if val is not None:
        # Strip out pair end quotes so e.g. -foo="bar baz" resulting in
        # \"bar baz \" would return without quotes which is more natural
        return _unquote(val)

    return val


type_parsers = {
    int: integer,
    str: string,
    bool: boolean,
}


class ArgumentConfigParser(ArgumentParser):
    def error(self, message):
        raise ConfigError(message)


def load_flags(fields: Iterable[Field]) -> Dict[str, str]:
    p = ArgumentConfigParser()
    for f in fields:
        try:
            # Use append to support specifying argument multiple times
            kwargs = {"action": "append", "nargs": "?", "type": type_parsers[f.type]}
        except KeyError:
            raise ConfigError(f"type {f.type} is not supported")

        if f.type == bool:
            kwargs["const"] = ""
            # Add --no- version of the flag to support setting falsy values
            p.add_argument(
                f"--no-{f.name}", action="store_const", const=False, dest=f.name
            )

        p.add_argument(f"--{f.name}", **kwargs)  # type: ignore

    parsed, _ = p.parse_known_args()

    result = {}
    for k, v in parsed.__dict__.items():
        val = v
        if isinstance(v, list):
            if len(v) > 1:
                raise ConfigError(f"--{k} specified multiple times")

            if len(v) != 0:
                val = v[0]

        if val is not None:
            result[k] = val

    return result
