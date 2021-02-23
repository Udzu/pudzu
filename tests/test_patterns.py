import pytest

from pudzu.sandbox.patterns import *


@pytest.mark.parametrize(
    "regex_a,regex_b",
    [
        ["a*", "a*a*"],
        ["a|b", "[ab]"],
    ],
)
def test_regex_simplification(regex_a, regex_b):
    """Check that two regexes simplify to the same thing."""
    assert regex(regex_a) == regex(regex_b)


@pytest.mark.parametrize(
    "regex_in,regex_out",
    [
        ["aa*", "(a+)"],
    ],
)
def test_regex_formatting(regex_in, regex_out):
    """Check that a regex has the expected string representation."""
    assert str(regex(regex_in)) == regex_out
