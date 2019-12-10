from argparse import ArgumentParser
from dataclasses import Field
from typing import Dict, Iterable

from magiconf.errors import ConfigError


def boolean(val):
    if val is None or val == "":
        return True

    if val in ("true", "True"):
        return True

    if val in ("false", "False"):
        return False

    raise ConfigError(f"{val} is not a boolean value")


class ArgumentConfigParser(ArgumentParser):
    def error(self, message):
        raise ConfigError(message)


def load_flags(fields: Iterable[Field]) -> Dict[str, str]:
    p = ArgumentConfigParser()
    for f in fields:
        # Use append to support specifying argument multiple times
        kwargs = {"action": "append", "type": f.type, "nargs": "?"}
        if f.type == bool:
            # We don't use store_true as it sets up False as default value
            # which might me unwanted, e.g. when default value in class is set
            # to True
            kwargs = {
                "action": "append",
                "type": boolean,
                "nargs": "?",
                "const": "",
            }

            # Add --no- version of the flag to support setting falsy values
            p.add_argument(
                f"--no-{f.name}", action="store_const", const=False, dest=f.name
            )

        p.add_argument(f"--{f.name}", **kwargs)  # type: ignore

    parsed, _ = p.parse_known_args()

    result = {}
    for k, v in parsed.__dict__.items():
        if v is None:
            continue

        if isinstance(v, list):
            if len(v) > 1:
                raise ConfigError(f"--{k} specified multiple times")

            if len(v) != 0:
                result[k] = v[0]
        else:
            result[k] = v

    return result
