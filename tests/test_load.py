from dataclasses import dataclass, fields
from unittest.mock import patch

from pytest import raises  # type: ignore

from magiconf import ConfigError, _load
from magiconf.env import load_env
from magiconf.flags import load_flags


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


class TestLoadBoolean:
    @dataclass
    class Config:
        foo: bool

    def test_load_default(self):
        @dataclass
        class Config:
            foo: bool = False

        with patch("sys.argv", "prog"), patch("os.environ", {}):
            flags = load_flags(fields(Config))
            env = load_env(fields(Config))
            assert _load(Config, [flags, env]).foo is False

    def test_fails_if_required_missing(self):
        with patch("sys.argv", "prog"), patch("os.environ", {}):
            flags = load_flags(fields(self.Config))
            env = load_env(fields(self.Config))
            with raises(ConfigError, match="is missing"):
                _load(self.Config, [flags, env])

    def test_first_source_takes_precedence(self):
        with patch("sys.argv", ["prog", "--foo=True"]):
            with patch("os.environ", {"foo": "False"}):
                flags = load_flags(fields(self.Config))
                env = load_env(fields(self.Config))
                cfg = _load(self.Config, [flags, env])
                assert cfg.foo is True

    def test_fall_back_to_second(self):
        with patch("sys.argv", ["prog"]):
            with patch("os.environ", {"foo": "true"}):
                flags = load_flags(fields(self.Config))
                env = load_env(fields(self.Config))
                cfg = _load(self.Config, [flags, env])
                assert cfg.foo is True
