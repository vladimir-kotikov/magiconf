import os
from unittest.mock import patch

from magiconf import load_env


def test_ok():
    with patch("os.environ", {}):
        assert load_env(["foo", "bar"]) == {}

    env = {"foo": "quux", "bar": "blep"}
    with patch.dict(os.environ, env):
        res = load_env(["foo", "bar"])
        for k, v in env.items():
            assert res[k] == v


def test_prefix():
    env = {"prefix_foo": "quux", "PREFIX_bar": "blep", "baz": "blurp"}
    with patch.dict(os.environ, env):
        res = load_env(["foo", "bar", "baz"], env_prefix="prefix")
        assert res["foo"] == "quux"
        assert res["bar"] == "blep"
        assert "baz" not in res

        assert load_env(["foo"], "prefix_") == {"foo": "quux"}
        assert load_env(["foo"], "prefix____") == {"foo": "quux"}


def test_mixed_case():
    items = ["foo", "bar", "baz"]
    env = {"foo": "quux", "BAR": "blep", "Baz": "blurp", "OtherVar": "asdasdasd"}
    with patch.dict(os.environ, env):
        assert load_env(items) == {"foo": "quux", "bar": "blep", "baz": "blurp"}
