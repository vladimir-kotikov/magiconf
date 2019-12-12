from dataclasses import dataclass, fields
from unittest.mock import patch

from pytest import raises  # type: ignore

from magiconf import ConfigError, load_flags


@dataclass
class Config:
    foo: str
    bar: int
    baz: bool


def test_no_args():
    with patch("sys.argv", ["prog"]):
        assert load_flags(fields(Config)) == {}


def test_ignores_unknown_args():
    with patch("sys.argv", ["prog", "--fubard", "snafu"]):
        assert load_flags(fields(Config)) == {}


def test_rejects_ambiguous_flags():
    with patch("sys.argv", ["prog", "--baz=True", "--baz=false", "--baz"]):
        with raises(ConfigError, match="--baz"):
            load_flags(fields(Config))


class TestBoolean:
    def test_raises_on_invalid_value(self):
        with raises(ConfigError):
            with patch("sys.argv", ["prog", "--baz=quux"]):
                load_flags(fields(Config))

    def test_parses_bool_flag(self):
        with patch("sys.argv", ["prog", "--baz"]):
            assert load_flags(fields(Config)) == {"baz": True}

        for t in ("True", "true"):
            with patch("sys.argv", ["prog", f"--baz={t}"]):
                assert load_flags(fields(Config)) == {"baz": True}

        for f in ("False", "false"):
            with patch("sys.argv", ["prog", f"--baz={f}"]):
                assert load_flags(fields(Config)) == {"baz": False}

    def test_parses_negated_flag(self):
        with patch("sys.argv", ["prog", "--no-baz"]):
            assert load_flags(fields(Config)) == {"baz": False}


class TestString:
    def test_with_no_value(self):
        with patch("sys.argv", ["prog", "--foo"]):
            assert load_flags(fields(Config)) == {}

    def test_parses_string_flag(self):
        with patch("sys.argv", ["prog", "--foo", "bar"]):
            assert load_flags(fields(Config)) == {"foo": "bar"}

        with patch("sys.argv", ["prog", "--foo=bar"]):
            assert load_flags(fields(Config)) == {"foo": "bar"}

    def test_parses_strings_with_whitespace(self):
        with patch("sys.argv", ["prog", "--foo", "bar baz quux"]):
            assert load_flags(fields(Config)) == {"foo": "bar baz quux"}

        with patch("sys.argv", ["prog", '--foo="bar baz quux"']):
            assert load_flags(fields(Config)) == {"foo": "bar baz quux"}

    def test_parses_strings_with_quotes(self):
        with patch("sys.argv", ["prog", "--foo", 'bar="baz"']):
            assert load_flags(fields(Config)) == {"foo": 'bar="baz"'}
