import os
from dataclasses import Field
from typing import Any, Dict, Iterable, Optional

from magiconf.errors import ConfigError
from magiconf.types import type_parsers


def load_env(
    fields: Iterable[Field], env_prefix: Optional[str] = None
) -> Dict[str, Any]:
    prefix = ""
    if env_prefix is not None:
        prefix = env_prefix
        # Make sure there's a trailing underscore
        if not prefix.endswith("_"):
            prefix = prefix + "_"

    result = {}
    for f in fields:
        val_name = prefix + f.name
        val = os.getenv(val_name, os.getenv(val_name.upper()))
        if val is None:
            continue

        try:
            parser = type_parsers[f.type]
        except KeyError:
            raise ConfigError(f"type {f.type} is not supported")

        result[f.name] = parser(val)

    return result
