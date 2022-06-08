import fnmatch
import glob
import logging
import operator
import re
from contextlib import nullcontext

import numpy as np
import pandas as pd
from pudzu.utils import *
from pudzu.utils import identity, ignoring_exceptions, ignoring_extra_args, nnn, non, non_string_iterable, optional_import

tqdm = optional_import("tqdm")
pyparsing = optional_import("pyparsing")

logger = logging.getLogger("bamboo")

# Various pandas utility functions


def _tqdm_wrapper(t, func, *args, **kwargs):
    t.update(1)
    return func(*args, **kwargs)


def _make_filter(filter):
    return ignoring_extra_args((lambda: True) if filter is None else filter if callable(filter) else FilterExpression.make_filter(filter))


def _filter_rows(df, filter):
    """Filter rows using either a row/index predicate or a RecordFilter expression. Slower than boolean indexing."""
    filter_fn = _make_filter(filter)
    return df[[filter_fn(r, i) for i, r in df.iterrows()]]


def _assign_rows(df, progressbar=False, assign_if=None, **kwargs):
    """Assign or update columns using row/index function, with an optional row/index predicate condition. Progress bars require tqdm."""
    filter_fn = _make_filter(assign_if)
    if progressbar and tqdm:
        t = tqdm.tqdm(total=len(df) * len(kwargs))
        filter_fn = partial(_tqdm_wrapper, t, filter_fn)
    results = df.assign(
        **{
            k: (lambda df, k=k, fn=fn: [(ignoring_extra_args(fn)(r, i) if callable(fn) else fn) if filter_fn(r, i) else r.get(k) for i, r in df.iterrows()])
            for k, fn in kwargs.items()
        }
    )
    if progressbar and tqdm:
        t.close()
    return results


def _update_columns(df, progressbar=False, update_if=None, **kwargs):
    """Update columns using a value function, with an optional value predicate condition, or True to update just non-nans. Progress bars require tqdm."""
    filter_fn = lambda v: (update_if is None or callable(update_if) and update_if(v) or isinstance(update_if, bool) and update_if != non(v))
    if progressbar and tqdm:
        t = tqdm.tqdm(total=len(df) * len(kwargs))
        filter_fn = partial(_tqdm_wrapper, t, filter_fn)
    results = df.assign(
        **{
            k: (lambda df, k=k, fn=fn: [(fn(r[k]) if callable(fn) else fn) if filter_fn(r[k]) else r.get(k) for _, r in df.iterrows()])
            for k, fn in kwargs.items()
        }
    )
    if progressbar and tqdm:
        t.close()
    return results


def _groupby_rows(df, by):
    """Group rows using a row/index function, index map, index list or column name."""
    return df.groupby(lambda i: ignoring_extra_args(by)(df.ix[i], i) if callable(by) else by[i] if non_string_iterable(by) else df.ix[i].get(by))


def _split_columns(df, columns, delimiter, converter=identity):
    """Split column string values into tuples with the given delimiter."""
    return df.update_columns(
        **{column: ignoring_exceptions(lambda s: tuple(converter(x) for x in s.split(delimiter)), (), (AttributeError)) for column in make_iterable(columns)}
    )


def _explode_to_columns(df, column, append=True):
    """Transform each element of list-likes into a new column, with NaNs for unfilled columns."""
    max_length = df[column].apply(ignoring_exceptions(len, 0)).max()
    new_cols = {f"{column}_{i}": df[column].apply(ignoring_exceptions(lambda v, j=i: v[j], np.nan)) for i in range(max_length)}
    df = df.assign(**new_cols)
    return df if append else df[list(new_cols)]


def _combine_columns(df, columns):
    """Combine columns into a tuple, ignoring NaNs and Nones, returning a series."""
    return df[columns].apply(lambda s: tuple(x for x in s if nnn(x)), axis=1)


pd.DataFrame.filter_rows = _filter_rows
pd.DataFrame.assign_rows = _assign_rows
pd.DataFrame.update_columns = _update_columns
pd.DataFrame.groupby_rows = _groupby_rows
pd.DataFrame.split_columns = _split_columns
pd.DataFrame.explode_to_columns = _explode_to_columns
pd.DataFrame.combine_columns = _combine_columns


def _reduce(groupby, fn):
    """Reduce a groupby by applying a function to every column."""
    return groupby.apply(lambda df: df.apply(fn))


pd.core.groupby.DataFrameGroupBy.reduce = _reduce

# standalone functions


def prompt_for_value(default=np.nan, prompt=lambda r: r.to_dict()):
    """Row update function for a new field value.
    - default is either a value or a function on rows, used when no value is provided.
    - prompt is either a function on rows."""
    defaulter = default if callable(default) else lambda r: default

    def updater(r):
        v = input("[{}] = ".format(prompt(r)))
        if v == "":
            v = defaulter(r)
        return v

    return updater


def read_csvs(files, *args, **kwargs):
    """Read and concatenate multiple csv files"""
    return pd.concat([pd.read_csv(file, *args, **kwargs) for file in glob.glob(files)], ignore_index=True)


def pd_print(item, **kwargs):
    """Print a value using the given pandas display options (e.g. min_rows=60)."""
    options = [[f"display.{k}", v] for k, v in kwargs.items()]
    with pd.option_context(*[v for o in options for v in o]) if options else nullcontext():
        print(item)


# filter expressions

if pyparsing:
    from pyparsing import CaselessLiteral, Combine, Literal, Optional, QuotedString, Word, alphas, alphas8bit, nums, oneOf, opAssoc, infixNotation

    class FilterExpression:
        """Filter factory based on filter expressions such as "name~John and (age>18 or consent:true)".
        Filters consist of:
            - boolean expressions using and, not, or and parentheses.
            - field expressions, which consist of:
              - a key name (with optional wildcards) or _index_
              - an operator
              - a value (with type appropriate to the operator)
            - operators are one of:
              - numeric comparisons: =, !=, <, <=, >, >=
              - length comparisons: #=, #<, etc
              - string comparisons: =, !=, ~ (regex match), !~
              - containment: >> (contains), !>>
              - existence: KEY:exists (has value that's not NaN or None), KEY:true (has true value)
        """

        sign = oneOf("+ -")
        integer = Word(nums)
        number_base = (integer + Optional("." + Optional(integer))("float")) | Literal(".")("float") + integer
        number_exponent = CaselessLiteral("E")("float") + Optional(sign) + integer
        number = Combine(Optional(sign) + number_base + Optional(number_exponent)).setParseAction(lambda t: float(t[0]) if t.float else int(t[0]))

        onlen = lambda f: (lambda x, y: f(len(x), y))

        num_ops = {
            "<": operator.lt,
            "<=": operator.le,
            "=": operator.eq,
            "!=": operator.ne,
            ">": operator.gt,
            ">=": operator.ge,
            "#<": onlen(operator.lt),
            "#<=": onlen(operator.le),
            "#=": onlen(operator.eq),
            "#!=": onlen(operator.ne),
            "#>": onlen(operator.gt),
            "#>=": onlen(operator.ge),
        }
        str_ops = {
            "=": lambda x, y: x == str(y),
            "!=": lambda x, y: x != str(y),
            "~": lambda x, y: re.search(y, str(x)),
            "!~": lambda x, y: not re.search(y, str(x)),
            ">>": lambda x, y: y in x,
            "!>>": lambda x, y: y not in x,
        }
        exist_ops = {":": lambda x, y: {"exists": not non(x), "true": bool(x)}[y.lower()]}

        oneOfOpMap = lambda map: oneOf(list(map.keys())).setParseAction(lambda t: ignoring_exceptions(map[t[0]], False))

        num_op = oneOfOpMap(num_ops)
        str_op = oneOfOpMap(str_ops)
        exist_op = oneOfOpMap(exist_ops)

        quoted_string = QuotedString('"', "\\") | QuotedString("'", "\\")
        key_value = Word(alphas + alphas8bit + "*?[]_") | quoted_string
        str_value = Word(alphas + alphas8bit + "_") | quoted_string
        exist_value = CaselessLiteral("True") | CaselessLiteral("Exists")

        base_expr = (key_value + (str_op + str_value | num_op + number | exist_op + exist_value)).setParseAction(lambda t: [t])
        expr = infixNotation(
            base_expr,
            [
                (Literal("not").setParseAction(lambda t: operator.not_), 1, opAssoc.RIGHT),
                (Literal("and").setParseAction(lambda t: operator.and_), 2, opAssoc.LEFT),
                (Literal("or").setParseAction(lambda t: operator.or_), 2, opAssoc.LEFT),
            ],
        )

        @classmethod
        def _eval_parse(cls, parse, d, i):
            if not isinstance(parse, list):
                return parse
            elif len(parse) == 1:
                return cls._eval_parse(parse[0], d, i)
            elif callable(parse[0]):
                return parse[0](cls._eval_parse(parse[1], d, i))
            else:
                x, y = cls._eval_parse(parse[0], d, i), cls._eval_parse(parse[2], d, i)
                if x == "_index_":
                    return parse[1](i, y)
                elif isinstance(x, str):
                    return any(parse[1](d[k], y) for k in d.keys() if fnmatch.fnmatch(k, x))
                else:
                    return parse[1](x, y)

        @classmethod
        def make_filter(cls, string):
            """Generates a filter function from a filter expression."""
            parse = cls.expr.parseString(string, parseAll=True).asList()
            return lambda d, i=None: cls._eval_parse(parse, d, i)
