import os
from argparse import ArgumentParser
from configparser import ConfigParser
from dataclasses import MISSING, fields
from typing import Any, Dict, List, Optional, Type, TypeVar


class ConfigError(Exception):
    pass


T = TypeVar("T")


def load_flags(flags: List[str]) -> Dict[str, str]:
    parser = ArgumentParser()
    for f in flags:
        parser.add_argument(f"--{f}")

    parsed, _ = parser.parse_known_args()
    return {k: v for k, v in parsed.__dict__.items() if v is not None}


def load_env(fields: List[str], env_prefix: Optional[str] = None) -> Dict[str, str]:
    prefix, prefixed_fields = "", [*fields]
    if env_prefix is not None:
        prefix = f"{env_prefix.rstrip('_')}_"
        prefixed_fields = [(prefix + name).lower() for name in fields]

    return {
        k.lower()[len(prefix) :]: v
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
    content = ""
    try:
        with open("config.ini", "r") as f:
            content = f.read()
    except IOError:
        pass

    sources = [
        load_flags(field_names),
        load_env(field_names, env_prefix),
        load_config(field_names, content),
    ]
    return _load(conf_cls, sources)


def _load(conf_cls: Type[T], sources: List[Dict[str, Any]]) -> T:
    init_kw = {}
    for field in fields(conf_cls):
        for src in sources:
            if field.name in src:
                init_kw[field.name] = src[field.name]
                break
        else:
            if field.default == MISSING and field.default_factory == MISSING:
                raise ConfigError(f"{field.name} is required but is missing")

        if field.name in init_kw and not isinstance(init_kw[field.name], field.type):
            raise TypeError(
                f"{field.name} is of wrong type ({type(init_kw[field.name])}, expected {field.type})"
            )

    return conf_cls(**init_kw)
