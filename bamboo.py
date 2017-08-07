import fnmatch
import math
import operator
import pandas as pd

from utils import *

if optional_import("pyparsing"): from pyparsing import *

logger = logging.getLogger('bamboo')

# Various pandas utility functions

def _row_filter(df, filter):
    """Filter rows using either a row predicate or a RecordFilter expression."""
    df_filter = filter if callable(filter) else FilterExpression.make_filter(filter) 
    return df[df.apply(df_filter, axis=1)]

def _key_filter(df, filter):
    """Filter rows using either a list of keys or a key predicate."""
    return df.select(filter, axis=1) if callable(filter) else df.filter(make_iterable(filter), axis=1)

def _row_assign(df, assign_if=None, **kwargs):
    """Assign or update columns using row function, with an optional row predicate condition."""
    return df.assign(**{k : (lambda df: [fn(r) if (assign_if is None or assign_if(r)) else r.get(k) for _,r in df.iterrows()]) for k,fn in kwargs.items()})

def _column_update(df, update_if=None, **kwargs):
    """Update columns using a value function, with an optional value predicate condition."""
    return df.assign(**{k : (lambda df: [fn(r[k]) if (update_if is None or update_if(r[k])) else r.get(k) for _,r in df.iterrows()]) for k,fn in kwargs.items()})
    
def _row_groupby(df, by):
    """Group rows using a row function, map, list or column name."""
    return df.groupby(lambda i: by(df.ix[i]) if callable(by) else by[i] if non_string_iterable(by) else df.ix[i].get(by))

def _column_split(df, by):
    """Split rows by column, making one copy for each item in the column value."""
    return pd.DataFrame(pd.Series(assoc_in(row, [by], v)) for _, row in df.iterrows() for v in make_iterable(row[by]))

# todo: tabulation
    
pd.DataFrame.filter_keys = _key_filter
pd.DataFrame.filter_rows = _row_filter
pd.DataFrame.assign_row = _row_assign
pd.DataFrame.groupby_row = _row_groupby
pd.DataFrame.update_column = _column_update
pd.DataFrame.split_column = _column_split

# filter expressions

class FilterExpression:
    """Filter factory based on filter expressions such as "name~John and (age>18 or consent:true)".
    Filters consist of:
        - boolean expressions using and, not, or and parentheses.
        - field expressions, which consist of:
          - a key name (with optional wildcards)
          - an operator
          - a value (with type appropriate to the operator)
        - operators are one of:
          - numeric comparisons: =, !=, <, <=, >, >=
          - length comparisons: #=, #<, etc
          - string comparisons: =, !=, ~ (regex match), !~
          - containment: >> (contains), !>>
          - existence: KEY:exists (has value that's not NaN), KEY:true (has true value)
    """
    
    sign = oneOf('+ -')
    integer = Word(nums)
    number_base = (integer + Optional('.' + Optional(integer))('float')) | Literal('.')('float') + integer
    number_exponent = CaselessLiteral('E')('float') + Optional(sign) + integer
    number = Combine( Optional(sign) + number_base + Optional(number_exponent) ).setParseAction(lambda t: float(t[0]) if t.float else int(t[0]))

    def onlen(f): return lambda x,y: f(len(x), y)
    num_ops = { '<': operator.lt, '<=': operator.le,
                '=': operator.eq, '!=': operator.ne,
                '>': operator.gt, '>=': operator.ge,
                '#<': onlen(operator.lt), '#<=': onlen(operator.le),
                '#=': onlen(operator.eq), '#!=': onlen(operator.ne),
                '#>': onlen(operator.gt), '#>=': onlen(operator.ge) }
    str_ops = { '=': lambda x,y: x==str(y), '!=': lambda x,y: x!=str(y),
                '~': lambda x,y: re.search(y,str(x)), '!~': lambda x,y: not re.search(y,str(x)),
                '>>': lambda x,y: y in x, '!>>': lambda x,y: y not in x }
    exist_ops = { ':': lambda x,y: { 'exists': not (isinstance(x, float) and math.isnan(x)), 'true': bool(x) }[y.lower()] }
                
    def oneOfOpMap(map): return oneOf(list(map.keys())).setParseAction(lambda t: ignoring_exceptions(map[t[0]], False))
    num_op = oneOfOpMap(num_ops)
    str_op = oneOfOpMap(str_ops)
    exist_op = oneOfOpMap(exist_ops)

    quoted_string = QuotedString('"', '\\') | QuotedString("'", '\\')
    key_value = Word(alphas + alphas8bit + '*?[]') | quoted_string
    str_value = Word(alphas + alphas8bit) | quoted_string
    exist_value = CaselessLiteral('True') | CaselessLiteral('Exists')

    base_expr = (key_value + ( str_op + str_value | num_op + number | exist_op + exist_value)).setParseAction(lambda t: [t])
    expr = operatorPrecedence(base_expr, [(Literal('not').setParseAction(lambda t: operator.not_), 1, opAssoc.RIGHT),
                                          (Literal('and').setParseAction(lambda t: operator.and_), 2, opAssoc.LEFT),
                                          (Literal('or').setParseAction(lambda t: operator.or_), 2, opAssoc.LEFT)])

    @classmethod
    def _eval_parse(cls, parse, d):
        if not isinstance(parse, list):
            return parse
        elif len(parse) == 1:
            return cls._eval_parse(parse[0], d)
        elif callable(parse[0]):
            return parse[0](cls._eval_parse(parse[1], d))
        else:
            x, y = cls._eval_parse(parse[0], d), cls._eval_parse(parse[2], d)
            if isinstance(x, str):
                return any(parse[1](d[k], y) for k in d.keys() if fnmatch.fnmatch(k, x))
            else:
                return parse[1](x, y)
            
    @classmethod
    def make_filter(cls, string):
        """Generates a filter function from a filter expression."""
        parse = cls.expr.parseString(string, parseAll=True).asList()
        return lambda d: cls._eval_parse(parse, d)

# Testing

rs = [ { "name": "Fred", "surname": "Flintstone", "children": 2, "childname": ["Pebbles", "Stony"] },
       { "name": "Wilma", "surname": "Flintstone", "children": 2, "childname": ["Pebbles", "Stony"] },
       { "name": "Dino", "children": 15 } ]
df = pd.DataFrame(rs)
