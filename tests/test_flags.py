from magiconf import load_flags
from unittest.mock import patch


def test_ok():
    assert load_flags(["foo", "bar"]) == {}
    with patch("sys.argv", ["prog", "--foo", "bruh"]):
        assert load_flags(["foo", "bar"]) == {"foo": "bruh"}


def test_ignores_unknown_args():
    with patch("sys.argv", ["prog", "--fubard", "snafu"]):
        assert load_flags(["foo", "bar"]) == {}
