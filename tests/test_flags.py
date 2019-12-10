from magiconf import load_flags, ConfigError
from unittest.mock import patch
from dataclasses import dataclass, fields
from pytest import raises  # type: ignore


@dataclass
class Config:
    foo: str
    bar: int
    baz: bool


def test_ok():
    assert load_flags(fields(Config)) == {}


def test_ignores_unknown_args():
    with patch("sys.argv", ["prog", "--fubard", "snafu"]):
        assert load_flags(fields(Config)) == {}


class TestBoolean:
    def test_with_defaults(self):
        @dataclass
        class Config:
            foo: bool = True
            bar: bool = False

        with patch("sys.argv", ["prog"]):
            # Should be empty as load_flags is not concerned about default values
            assert load_flags(fields(Config)) == {}

    def test_with_required(self):
        with patch("sys.argv", ["prog"]):
            # Should not raise as this is a caller's responsibility
            assert load_flags(fields(Config)) == {}

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

    def test_rejects_multiple_flags(self):
        with patch("sys.argv", ["prog", "--baz=True", "--baz=false", "--baz"]):
            with raises(ConfigError, match="--baz"):
                load_flags(fields(Config))
