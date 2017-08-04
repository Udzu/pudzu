import pandas as pd

from utils import *
from records import *

logger = logging.getLogger('bamboo')

# Initially a translation of records.py to pandas. May turn into useful utilities.

def df_keys(df):
    return list(df.columns)
    
def df_values(df, key):
    return remove_duplicates(df[key])
    
# DEPRECATE: make_records, map_to_records

def filter_df(df, filter=None, key_filter=None):
    if filter is not None:
        record_filter = filter if callable(filter) else RecordFilter.make_filter(filter) 
        df = df[df.apply(record_filter, axis=1)]
    if key_filter is not None:
        if callable(key_filter):
            df = df.select(key_filter, axis=1)
        else:
            df = df.filter(make_iterable(key_filter), axis=1)
    return df

# TODO: progressbar

def update_with(**kwargs):
    return df.assign(**kwargs)

# def update_if(condition, fn, alt_fn=None):

# Testing

rs = [ { "name": "Fred", "surname": "Flintstone", "children": 2 },
       { "name": "Wilma", "surname": "Flintstone", "children": 2 },
       { "name": "Dino", "children": 15 } ]
df = pd.DataFrame(rs)

