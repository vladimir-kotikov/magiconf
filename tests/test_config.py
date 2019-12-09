from magiconf import load_config

config = """
[default]
foo = quux
bar = kaboom
baz = snafu
"""


def test_ok():
    assert load_config(["foo", "bar"], config) == {
        "foo": "quux",
        "bar": "kaboom",
    }
