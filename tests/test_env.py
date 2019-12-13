from dataclasses import dataclass, fields
from unittest.mock import patch

from pytest import mark, raises  # type: ignore

from magiconf import ConfigError, load_env


@dataclass
class Config:
    foo: str
    bar: int
    baz: bool


def test_ok():
    with patch("os.environ", {"foo": "quux", "bar": "10", "baz": "True"}):
        assert load_env(fields(Config)) == {"foo": "quux", "bar": 10, "baz": True}


def test_empty_env():
    with patch("os.environ", {}):
        assert load_env(fields(Config)) == {}


def test_ignores_unknown_env():
    assert load_env(fields(Config)) == {}


class TestNameCase:
    def test_prefers_same_case(self):
        with patch("os.environ", {"foo": "quux", "FOO": "blep"}):
            assert load_env(fields(Config)) == {"foo": "quux"}

    def test_tries_read_uppercase(self):
        with patch("os.environ", {"FOO": "blep"}):
            assert load_env(fields(Config)) == {"foo": "blep"}

    def test_mixed_case(self):
        env = {"foo": "quux", "BAR": "10", "Baz": "False"}
        with patch("os.environ", env):
            actual = load_env(fields(Config))
            assert actual == {"foo": "quux", "bar": 10}


class TestPrefix:
    @mark.parametrize("prefix", ["prefix", "prefix_"])
    def test_with_prefix(self, prefix):
        env = {"prefix_foo": "quux", "PREFIX_BAR": "10"}
        with patch("os.environ", env):
            actual = load_env(fields(Config), env_prefix=prefix)
            assert actual == {"foo": "quux", "bar": 10}

    def test_prefix_multiple_underscore(self):
        env = {"prefix__foo": "quux"}
        with patch("os.environ", env):
            actual = load_env(fields(Config), env_prefix="prefix__")
            assert actual == {"foo": "quux"}


class TestBoolean:
    def test_raises_on_invalid_value(self):
        with raises(ConfigError):
            with patch("os.environ", {"baz": "quux"}):
                load_env(fields(Config))

    @mark.parametrize("val", ["true", "True", "1"])
    def test_parses_bool_truthy_value(self, val):
        with patch("os.environ", {"baz": val}):
            assert load_env(fields(Config)) == {"baz": True}

    @mark.parametrize("val", ["false", "False", "0"])
    def test_parses_bool_falsy_value(self, val):
        with patch("os.environ", {"baz": val}):
            assert load_env(fields(Config)) == {"baz": False}


class TestString:
    def test_with_no_value(self):
        with patch("os.environ", {"foo": ""}):
            assert load_env(fields(Config)) == {"foo": ""}

    def test_parses_string(self):
        with patch("os.environ", {"foo": "bar"}):
            assert load_env(fields(Config)) == {"foo": "bar"}

    def test_parses_strings_with_whitespace(self):
        with patch("os.environ", {"foo": "bar baz quux"}):
            assert load_env(fields(Config)) == {"foo": "bar baz quux"}

    def test_parses_strings_with_quotes(self):
        with patch("os.environ", {"foo": 'bar="baz"'}):
            assert load_env(fields(Config)) == {"foo": 'bar="baz"'}


class TestInt:
    @mark.parametrize("val", ("10", "0b1010", "0o12", "0xa"))
    def test_parses_ok(self, val):
        with patch("os.environ", {"bar": val}):
            assert load_env(fields(Config)) == {"bar": 10}

    @mark.parametrize("val", ("-10", "-0b1010", "-0o12", "-0xa"))
    def test_parses_negative_numbers(self, val):
        with patch("os.environ", {"bar": val}):
            assert load_env(fields(Config)) == {"bar": -10}

    def test_fails_on_invalid_value(self):
        with raises(ConfigError):
            with patch("os.environ", {"bar": "no"}):
                load_env(fields(Config))
