import pandas as pd

from utils import *
from records import *

logger = logging.getLogger('bamboo')

# Various pandas utility functions

def _value_filter(df, filter):
    """Filter rows using either a row predicate or a RecordFilter expression."""
    df_filter = filter if callable(filter) else RecordFilter.make_filter(filter) 
    return df[df.apply(df_filter, axis=1)]

def _key_filter(df, filter):
    """Filter rows using either a list of keys or a key predicate."""
    return df.select(filter, axis=1) if callable(filter) else df.filter(make_iterable(filter), axis=1)

def _row_assign(df, assign_if=None, **kwargs):
    """Assign or update columns using row function, with an optional row predicate condition."""
    return df.assign(**{k : (lambda df: [fn(r) if (assign_if is None or assign_if(r)) else r.get(k) for _,r in df.iterrows()]) for k,fn in kwargs.items()})

pd.DataFrame.value_filter = _value_filter
pd.DataFrame.key_filter = _key_filter
pd.DataFrame.row_assign = _row_assign

# Testing

rs = [ { "name": "Fred", "surname": "Flintstone", "children": 2 },
       { "name": "Wilma", "surname": "Flintstone", "children": 2 },
       { "name": "Dino", "children": 15 } ]
df = pd.DataFrame(rs)
