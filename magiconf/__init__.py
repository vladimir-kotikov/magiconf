from configparser import ConfigParser
from dataclasses import MISSING, fields
from typing import Any, Dict, List, Optional, Type, TypeVar

from magiconf.env import load_env
from magiconf.errors import ConfigError
from magiconf.flags import load_flags

T = TypeVar("T")


def load_config(
    fields: List[str], content: str, section: str = "default"
) -> Dict[str, str]:
    parser = ConfigParser()
    parser.read_string(content)
    # TODO: support sections
    return {k: v for k, v in parser.items(section) if k in fields}


def load(conf_cls: Type[T], env_prefix: Optional[str] = None):
    sources: List[Dict[str, Any]] = [
        load_flags(fields(conf_cls)),
        load_env(fields(conf_cls), env_prefix),
    ]

    try:
        with open("config.ini", "r") as f:
            content = f.read()
            field_names = [f.name for f in fields(conf_cls)]
            sources.append(load_config(field_names, content))
    except IOError:
        pass

    return _load(conf_cls, sources)


def _load(conf_cls: Type[T], sources: List[Dict[str, Any]]) -> T:
    init_kw = {}
    for field in fields(conf_cls):
        for src in sources:
            if field.name in src:
                init_kw[field.name] = src[field.name]
                break
        else:
            is_requried = (
                getattr(field, "default", None) == MISSING
                and getattr(field, "default_factory", None) == MISSING
            )
            if is_requried:
                raise ConfigError(f"{field.name} is required but is missing")

        if field.name in init_kw and not isinstance(init_kw[field.name], field.type):
            raise TypeError(
                "{} is of wrong type ({}, expected {})".format(
                    field.name, type(init_kw[field.name]), field.type
                )
            )

    return conf_cls(**init_kw)  # type: ignore
