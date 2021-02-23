import itertools
import operator
import re

import bs4
from pudzu.utils import *

# Various utilities for BeautifulSoup

# helper functions since: (a) bs4 tags need to be compared with is, not eq; (b) they're iterable


def remove_duplicate_tags(l):
    """Remove duplicate tags from a list (using object identity rather than equality)"""
    return remove_duplicates(l, key=id)


def non_bs4_iterable(v):
    """Whether an object is a non-bs4 iterable."""
    return non_string_iterable(v) and not hasattr(v, "find_all")


def make_bs4_iterable(v):
    """Return a non-bs4 iterable from an object, wrapping it in a tuple if needed."""
    return v if non_bs4_iterable(v) else (v,)


# pretty-printing tags


def print_tags(tags, attr=None):
    """Print one or more tags, excluding any nested content."""
    for tag in make_bs4_iterable(tags):
        if attr is not None:
            print(tag.attrs.get(attr, ""))
        elif hasattr(tag, "attr"):
            attrs = " ".join('{}="{}"'.format(k, " ".join(v) if non_string_iterable(v) else v) for k, v in sorted(tag.attrs.items()))
            print("<{}{}{}>".format(tag.name, "" if len(tag.attrs) == 0 else " ", attrs))
        else:
            print(tag)


def print_path(tag):
    """Print the path from the root down to a tag."""
    print_tags(list(itertools.chain([tag], tag.parents))[-2::-1])


pt = print_tags
pp = print_path

# filtering


def re_exclude(pattern):
    """Negated regular expression filter."""
    pattern = re.compile(pattern)
    return lambda v: v and not re.search(pattern, v)


def is_parent(t, s):
    """Whether t is s's parent."""
    return t is s.parent


def is_child(t, s):
    """Whether t is s's child."""
    return s is t.parent


def is_ancestor(t, s):
    """Whether t is an ancestor of s."""
    return is_in(t, s.parents)


def is_descendent(t, s):
    """Whether t is a descendent of s."""
    return is_in(s, t.parents)


def is_after(t, s):
    """Whether t occurs after s."""
    return is_in(t, s.next_elements)


def is_before(t, s):
    """Whether t occurs before s."""
    return is_in(s, t.next_elements)


def exclude_tags(tags, excluded, relation=operator.is_):
    """Filter out tags that are related to at least one of the excluded set."""
    return [t for t in make_bs4_iterable(tags) if not any(relation(t, s) for s in make_bs4_iterable(excluded))]


def restrict_tags(tags, included, relation=operator.is_):
    """Restrict to tags that are related to at least one of the included set."""
    return [t for t in make_bs4_iterable(tags) if any(relation(t, s) for s in make_bs4_iterable(included))]


# finding tags by chaining


def curry_method(method):
    def fn(*args, **kwargs):
        return lambda o: method(o, *args, **kwargs)

    return fn


all_ = curry_method(bs4.element.Tag.find_all)
next_ = curry_method(bs4.element.Tag.find_all_next)
prev_ = curry_method(bs4.element.Tag.find_all_previous)
parents_ = curry_method(bs4.element.Tag.find_parents)
next_siblings_ = curry_method(bs4.element.Tag.find_next_siblings)
prev_siblings_ = curry_method(bs4.element.Tag.find_previous_siblings)
select_ = curry_method(bs4.element.Tag.select)
exclude_ = curry_method(exclude_tags)
restrict_ = curry_method(restrict_tags)


def find_tags(tags, *fns):
    """Apply a chain sequence of find methods to a collection of tags. Result may contain duplicates."""
    ts = make_bs4_iterable(tags)
    for fn in fns:
        if not callable(fn):
            fn = all_(fn)
        ts = [s for t in ts for s in make_bs4_iterable(fn(t))]
    return ts


def find_tag(tags, *fns):
    """Same as find_tags but returns the first result only (or None if there are none)."""
    return first(find_tags(tags, *fns))
