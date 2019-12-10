import os
from configparser import ConfigParser
from dataclasses import MISSING, fields
from typing import Any, Dict, List, Optional, Type, TypeVar

from magiconf.flags import load_flags
from magiconf.errors import ConfigError


T = TypeVar("T")


def load_env(fields: List[str], env_prefix: Optional[str] = None) -> Dict[str, str]:
    prefix, prefixed_fields = "", [*fields]
    if env_prefix is not None:
        prefix = f"{env_prefix.rstrip('_')}_"
        prefixed_fields = [(prefix + name).lower() for name in fields]

    return {
        # fmt: off
        k.lower()[len(prefix):]: v
        # fmt: on
        for k, v in os.environ.items()
        if k.lower() in prefixed_fields
    }


def load_config(
    fields: List[str], content: str, section: str = "default"
) -> Dict[str, str]:
    parser = ConfigParser()
    parser.read_string(content)
    # TODO: support sections
    return {k: v for k, v in parser.items(section) if k in fields}


def load(conf_cls: Type[T], env_prefix: Optional[str] = None):
    field_names = [f.name for f in fields(conf_cls)]
    sources: List[Dict[str, Any]] = [
        load_flags(fields(conf_cls)),
        load_env(field_names, env_prefix),
    ]

    try:
        with open("config.ini", "r") as f:
            content = f.read()
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
