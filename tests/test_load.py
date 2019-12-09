from dataclasses import dataclass
from magiconf import _load, ConfigError
from pytest import raises  # type: ignore


@dataclass
class Config:
    foo: str
    bar: str = "baz"


def test_ok():
    cfg = _load(Config, [{"foo": "foo", "bar": "bar"}])
    assert cfg.foo == "foo"
    assert cfg.bar == "bar"


def test_default_values():
    cfg = _load(Config, [{"foo": "foo"}])
    assert cfg.foo == "foo"
    assert cfg.bar == "baz"


def test_extra_values():
    cfg = _load(Config, [{"foo": "foo", "quux": "blep"}])
    assert cfg.foo == "foo"
    assert cfg.bar == "baz"


def test_wrong_type():
    with raises(TypeError):
        _load(Config, [{"foo": 100}])


def test_missing_required_value():
    with raises(ConfigError):
        _load(Config, [{}])


def test_multi_sources():
    cfg = _load(Config, [{"foo": "foo1"}, {"foo": "foo2", "bar": "bar2"}])
    assert cfg.foo == "foo1"
    assert cfg.bar == "bar2"
