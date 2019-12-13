from argparse import ArgumentParser
from dataclasses import Field
from typing import Dict, Iterable

from magiconf.errors import ConfigError
from magiconf.types import type_parsers


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
