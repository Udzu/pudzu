import pytest

from pudzu.sandbox.patterns import *


@pytest.mark.parametrize(
    "regex_a,regex_b",
    [
        ["a|b|b", "[ab]"],
        ["[ab]|[ac]", "[abc]"],
        ["a*a*", "a*"],
        ["a*aa*", "a+"],
        ["(a*)*", "a*"],
        ["a|b|a*", "b|a*"],
        ["ab|ac", "a(b|c)"],
        ["ab|ac|a", "a(b|c)?"],
        ["ba|ca", "(b|c)a"],
        ["ba|ca|a", "(b|c)?a"],
        ["(a*b*c*)*", "(a|b|c)*"],
        ["(aa|a)*", "a*"],
        ["(a|b*)*", "(a|b)*"],
        ["(a*|b*|c*)*", "(a|b|c)*"],
    ],
)
def test_regex_simplification(regex_a, regex_b):
    """Check that two regexes simplify to the same thing."""
    assert regex(regex_a) == regex(regex_b)


@pytest.mark.parametrize(
    "reg,reg_fmt",
    [
        ["aa*", "(a+)"],
    ],
)
def test_regex_formatting(reg, reg_fmt):
    """Check that a regex has the expected string representation."""
    assert str(regex(reg)) == reg_fmt


@pytest.mark.parametrize(
    "reg,first_char,last_char",
    [
        ["the", "t", "e"],
        ["t?he*", "[th]", "[eh]"],
        ["the|a", "[ta]", "[ea]"],
        ["[^a]|a*", ".?", ".?"],
        [".{0}", ".{0}", ".{0}"],
    ],
)
def test_regex_first_character(reg, first_char, last_char):
    """Check that a regex has the expected first and last characters."""
    assert regex(reg).first_character() == regex(first_char)
    assert regex(reg).first_character(from_end=True) == regex(last_char)
