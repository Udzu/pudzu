import abc as ABC
import csv
import fnmatch
import glob
import json
import logging
import operator
import os
import re
import sqlite3

from collections import OrderedDict, Mapping
from enum import Enum
from functools import reduce
from itertools import islice, chain
from numbers import Real, Integral
from os.path import basename, splitext

from utils import *

pd = optional_import("pandas")
tqdm = optional_import("tqdm", tqdm=identity)
psycopg2 = optional_import("psycopg2")
psycopg2.extras = optional_import("psycopg2.extras")
if optional_import("pyparsing"): from pyparsing import *

# Various utilities for handling records (lists of dicts) and group maps (ordered dicts of records)

logger = logging.getLogger('records')

# Record manipulation

def record_keys(records):
    """Return all the keys used in the records."""
    return list(OrderedDict((k, None) for d in records for k in d).keys())
    
def record_values(records, key):
    """Return all the unique values used in the records for a given key."""
    return list(OrderedDict((d[key], None) for d in records if key in d))

def make_records(v):
    """Return a records list from an object."""
    return [make_mapping(d) for d in make_sequence(v)]
  
def map_to_records(d, key_name="key", value_name="value"):
    """Convert a mapping to a records lits."""
    return [{key_name:k, value_name:v} for k,v in d.items()]

def filter_records(records, filter=None, key_filter=None):
    """Returns a filtered copy of records.
    - filter is either a RecordFilter input or a function on dicts
    - key_filter is either field name(s) or a function on keys"""
    if filter is not None:
        record_filter = filter if callable(filter) else RecordFilter.make_filter(filter)
        records = [d for d in records if record_filter(d)]
    if key_filter is not None:
        predicate = key_filter if callable(key_filter) else lambda k: k in make_iterable(key_filter)
        records = [keyfilter(predicate, d) for d in records]
    return records

def update_records(records, fn, progressbar=False, break_on_error=True):
    """Returns an updated copy of records."""
    updated = list(records)
    for i in (tqdm.tqdm if progressbar else identity)(range(len(records))):
        try:
            updated[i] = fn(updated[i])
        except:
            logger.exception("Failed to update record #{}: {}".format(i, updated[i]))
            if break_on_error:
                logger.error("Bailing out")
                break
    return updated

def update_if(condition, fn, alt_fn=lambda d: d):
    """Conditional update function."""
    condition_fn = condition if callable(condition) else RecordFilter.make_filter(condition)
    def updater(d):
        if condition_fn(d): return fn(d)
        else: return alt_fn(d)
    return updater

def update_all(*fns):
    """Chained update function."""
    def updater(d):
        for fn in fns:
            d = fn(d)
        return d
    return updater
    
def update_with(replace_existing=True, **kwargs):
    """Add dictionary fields using given functions."""
    def updater(d):
        newd = d
        for field,value_fn in kwargs.items():
            field = field.rstrip('_')
            if field not in d or replace_existing:
                newval = value_fn(d)
                if newval is None: newd = dissoc(newd, field)
                else: newd = assoc_in(newd, [field], newval)
        return newd
    return updater
    
def prompt_for_value(field, default=None, prompt=lambda d, f: "{}/{}".format(d, f)):
    """Update function prompting for a new field value.
    - default is either a value or a function on dicts, used when no value is provided.
    If it returns None, then the field is removed.
    - prompt is a function on the record and field name."""
    defaulter = default if callable(default) else lambda d: default
    def updater(d):
        v = input('[{}] = '.format(ignoring_extra_args(prompt)(d, field)))
        if v == '': v = ignoring_extra_args(defaulter)(d, field)
        if v is None: return dissoc(d, field)
        else: return assoc_in(d, [field], v)
    return updater

def merge_records(*records, merge_key=None, merge_fn=lambda k, *vs: vs[-1]):
    """Combine collections of records, merging records with the same key
    via the merge function.
    - merge_key is either some field names or a function on dicts
    - merge_fn is a function on conflicting field names and values."""
    key_fn = merge_key if callable(merge_key) or merge_key is None else lambda d: tuple(d.get(k) for k in make_iterable(merge_key))
    merged_by_key = OrderedDict()
    for d in chain(*records):
        key = key_fn(d) if key_fn is not None else len(merged_by_key)
        merged_by_key.setdefault(key, []).append(d)
    return [merge_dicts(*ds, merge_fn=merge_fn) for ds in merged_by_key.values()]

# Group manipulation

def make_group_map(map_or_records, default_key=None):
    """Return the group map or wrap the records in a singleton map."""
    return map_or_records if isinstance(map_or_records, Mapping) else { default_key: map_or_records }
    
def group_records(records, group_by=None, groups=None, by_filter=False, split_iterable_keys=True):
    """Group records into a group map with group names extracted either from group_by (a field, function or iterable)
    or groups (a sequence). Records may be placed in multiple groups. If by_filter is True then group_by
    is interpreted as a filter on records and groups rather a group key."""
    if by_filter:
        filter = group_by if callable(group_by) else (lambda d, g: True) if group_by is None else (lambda d, g: d.get(group_by) == g)
        group_map = OrderedDict((g,[d for d in records if filter(d,g)]) for g in groups)
    else:
        grouper = group_by if callable(group_by) else (lambda d: groups) if group_by is None else (lambda d: d[1]) if non_string_iterable(group_by) else (lambda d: d.get(group_by))
        group_map = OrderedDict((g,[]) for g in (groups if groups is not None else []))
        for d in (zip(records, group_by) if non_string_iterable(group_by) else records):
            g = grouper(d)
            if g is None: continue
            for g in make_iterable(g) if split_iterable_keys else (g,):
                if groups is None or g in groups:
                    group_map.setdefault(g,[]).append(d[0] if non_string_iterable(group_by) else d)
    return group_map

def filter_groups(group_map, record_filter=None, key_filter=None, group_filter=None):
    """Filter group map using a record filter, key filter and group filter, which is a function
    on the group name and (filtered) group records."""
    predicate = group_filter if callable(group_filter) else lambda g,fr: g in make_iterable(group_filter)
    return OrderedDict((g,fr) for g,r in group_map.items()
                       for fr in [filter_records(r, record_filter, key_filter)]
                       if group_filter is None or predicate(g,fr))
    
def update_groups(group_map, record_update=lambda r: r, group_update=lambda g: g):
    """Update group map using a record update and group name update"""
    return OrderedDict((newg,ignoring_extra_args(record_update)(r,newg)) for g,r in group_map.items() for newg in (group_update(g),))
    
def sorted_groups(group_map, group_key=lambda k,v: k, group_reverse=False, record_key=None, record_reverse=False):
    """Sort a group map using a group key and record key for the group records."""
    record_sort = ((k,r if record_key is None else sorted(r, key=record_key, reverse=record_reverse)) for k,r in group_map.items())
    group_sort = sorted(record_sort, key=lambda kv: group_key(kv[0],kv[1]), reverse=group_reverse)
    return OrderedDict(group_sort)
    
def merge_groups(group_map, group_key=None, record_key=None, record_merge_fn=lambda k, *vs: vs[-1], group_label_field=None):
    """Combine groups inside a group map based on a group key, merging their records using record_key and
    record_merge_fn if required, and labeling the source group(s) in group_label_field."""
    grouper = group_key if callable(group_key) else lambda g: group_key
    new_map = OrderedDict()
    for g,rs in group_map.items():
        if group_label_field is not None:
            rs = update_records(rs, lambda d: assoc_in(d, [group_label_field], g))
        new_map.setdefault(grouper(g), []).append(rs)
    merge_fn = record_merge_fn
    if group_label_field is not None:
        def merge_fn(k, *vs):
            if k != group_label_field: return record_merge_fn(k, *vs)
            else: return list(vs)
    new_map = valmap(lambda rs: merge_records(*rs, merge_key=record_key, merge_fn=merge_fn), new_map, factory=OrderedDict)
    return new_map[None] if group_key is None else new_map
    
def records_to_dict(records, key):
    """Convert records into an ordered dict with a given key."""
    return update_groups(group_records(records, key), first_or_none)
    

# Tables (= Panda dataframes) - a bit confusing

def tabulate_records(records, row_group_by=None, rows=None, row_filter=False, col_group_by=None, columns=None, col_filter=False, fn=len):
    """Tabulate a record collection by grouping by rows and columns and calling a function at each intersection. Column grouping function
    can take an additional optional parameter named 'row'."""
    row_map = group_records(records, row_group_by, rows, row_filter)
    row_map = update_groups(row_map, lambda r,g: group_records(r, (partial(col_group_by, row=g) if callable(col_group_by) and 'row' in all_keyword_args(col_group_by) else col_group_by), columns, col_filter))
    rows = rows if rows is not None else list(row_map.keys())
    columns = columns if columns is not None else remove_duplicates(list(col for row in row_map.values() for col in row.keys())) if non_string_iterable(col_group_by) or (callable(col_group_by) and 'row' in all_keyword_args(col_group_by)) else list(group_records(records, col_group_by, columns, col_filter).keys())
    array = [[ignoring_extra_args(fn)(records, col, row) for col in columns for records in [col_map.get(col, [])]] for row in rows for col_map in [row_map.get(row, [])]]
    return pd.DataFrame(array, index=rows, columns=columns)

def tabulate_groups(group_map, subgroup_by=None, subgroups=None, subgroup_filter=False, transpose=False, fn=len):
    """Tabulate a group mapping by subgrouping and calling a function each intersection. Subgrouping function
    can take an additional optional parameter named 'supergroup'."""
    row_map = update_groups(group_map, lambda r,g: group_records(r, (partial(subgroup_by, supergroup=g) if callable(subgroup_by) and 'supergroup' in all_keyword_args(subgroup_by) else subgroup_by), subgroups, subgroup_filter))
    rows = list(row_map.keys())
    columns = subgroups if subgroups is not None else remove_duplicates(list(col for row in row_map.values() for col in row.keys()))
    array = [[ignoring_extra_args(fn)(records, row, col) for col in columns for records in [col_map.get(col, [])]] for row in rows for col_map in [row_map.get(row, [])]]
    df = pd.DataFrame(array, index=rows, columns=columns)
    return df.transpose() if transpose else df
   
def moving_average(key, radius, val=1, first_value=None, last_value=None, weighted=False):
    """Tabulation function for calculating a moving average. Expects numeric row groups containing
    all the records being averaged - the simplest is to generate them with just the rows parameter."""
    key_fn = key if callable(key) else lambda d: d.get(key)
    val_fn = val if callable(val) else lambda d: (d.get(val) if isinstance(val, str) else val)
    def wrapper(records, col, row):
        low = max([l for l in (first_value, row-radius) if l is not None])
        high = min([h for h in (last_value, row+radius) if h is not None])
        if low > high:
            return 0
        if not weighted:
            values = [val_fn(d) for d in records if low <= key_fn(d) <= high]
            size = high - low + 1
        else:
            def wgt(n): return radius + 1 - abs(n)
            def tri(n): return (n * (n+1)) // 2
            l, r = low-row, high-row
            values = [wgt(key_fn(d)-row) * val_fn(d) for d in records if low <= key_fn(d) <= high]
            size = (tri(wgt(min(0,r))) - tri(wgt(min(0,l-1))) +
                     tri(wgt(max(0,l))) - tri(wgt(max(0,r+1))) -
                     (wgt(0) if (l <= 0 <= r) else 0))
        return sum(values) / size
    return wrapper

# RecordFilter expressions

class RecordFilter:
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
          - existence: KEY:exists (exists), KEY:true (exists and has true value)
    """
    
    def oneOfOpMap(map): return oneOf(list(map.keys())).setParseAction(lambda t: ignoring_exceptions(map[t[0]], False))
    def onlen(f): return lambda x,y: f(len(x), y)
    
    sign = oneOf('+ -')
    integer = Word(nums)
    number_base = (integer + Optional('.' + Optional(integer))('float')) | Literal('.')('float') + integer
    number_exponent = CaselessLiteral('E')('float') + Optional(sign) + integer
    number = Combine( Optional(sign) + number_base + Optional(number_exponent) ).setParseAction(lambda t: float(t[0]) if t.float else int(t[0]))

    num_ops = { '<': operator.lt, '<=': operator.le,
                '=': operator.eq, '!=': operator.ne,
                '>': operator.gt, '>=': operator.ge,
                '#<': onlen(operator.lt), '#<=': onlen(operator.le),
                '#=': onlen(operator.eq), '#!=': onlen(operator.ne),
                '#>': onlen(operator.gt), '#>=': onlen(operator.ge) }
    str_ops = { '=': lambda x,y: x==str(y), '!=': lambda x,y: x!=str(y),
                '~': lambda x,y: re.search(y,str(x)), '!~': lambda x,y: not re.search(y,str(x)),
                '>>': lambda x,y: y in x, '!>>': lambda x,y: y not in x }
    exist_ops = { ':': lambda x,y: { 'exists': True, 'true': bool(x) }[y.lower()] }
                
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
                return any(parse[1](d[k], y) for k in d if fnmatch.fnmatch(k, x))
            else:
                return parse[1](x, y)
            
    @classmethod
    def make_filter(cls, string):
        """Generates a filter function from a filter expression."""
        parse = cls.expr.parseString(string, parseAll=True).asList()
        return lambda d: cls._eval_parse(parse, d)

# Record storage

class RecordFileBase(object):
    """Abstract base class for storing and loading records."""
    __metaclass__ = ABC.ABCMeta
    
    @classmethod
    @ABC.abstractmethod
    def load(cls, input, **kwargs):
        """Retrieve record data from the input source and return a dict sequence."""
    
    @classmethod
    def load_file(cls, filename, encoding='utf8', max_results=None, **kwargs):
        """Retrieve record data from file and return a dict sequence."""
        logger.info("Loading from {}".format(filename))
        with open(filename, 'r', encoding=encoding, newline=None) as input:
            return cls.load(input, **kwargs)[:max_results]

    @classmethod
    def load_files(cls, filenames, encoding='utf8', group_name=lambda f: splitext(basename(f))[0], **kwargs):
        """Retrieve record data from file glob and return a group map of dict sequence.
        Accepts an optional function for generating group names from file names."""
        group_map = OrderedDict()
        for file in glob.glob(filenames):
            group_map[group_name(file)] = cls.load_file(file, encoding=encoding, **kwargs)
        return group_map

    @classmethod
    @ABC.abstractmethod
    def save(cls, output, records, **kwargs):
        """Save the dict sequence to the output."""
        
    @classmethod
    def save_file(cls, filename, records, encoding='utf8', **kwargs):
        """Save the dict sequence to file."""
        logger.info("Saving to {}".format(filename))
        with open(filename, 'w', encoding=encoding, newline='') as output:
            cls.save(output, records, **kwargs)

    @classmethod
    def save_files(cls, file_names, group_map, base_dir=".", **kwargs):
        """Save a map of dict sequences into one file per entry. Accepts an
        optional filename template or function to generate file names from group names."""
        def default_namer(g):
            name, ext = ("", file_names) if file_names.rfind('.') == 0 else splitext(file_names)
            return name + g + ext
        namer = file_names if callable(file_names) else default_namer
        for group,records in group_map.items():
            cls.save_file(os.path.join(base_dir, namer(group)), records, **kwargs)
            
class RecordJSON(RecordFileBase):
    """Records stored as JSON."""
    
    @classmethod
    def load(self, input):
        return make_records(json.load(input))
    
    @classmethod
    def save(self, output, records):
        json.dump(records, output)

class RecordCSV(RecordFileBase):
    """Records stored as CSVs. Supports unnested arrays, bools, floats and ints via header type annotations."""
    
    TYPE_ANNOTATIONS = { 's': str, 'i': int, 'f': float, 'b': bool, 'n': type(None) }
    TYPE_NAMES = { t:s for s,t in TYPE_ANNOTATIONS.items() } 
    TYPE_PATTERN = re.compile(r"^(.*)_(a)?(.)$")
    
    @staticmethod
    def _cast(t, v):
        if t == bool: return v.lower() == 'true' or v == '1'
        elif t == type(None): return None
        else: return t(v)
        
    @staticmethod
    def _merge_types(s, t):
        if str in (s, t):          return str
        elif type(None) in (s, t): return s if t == type(None) else t
        elif bool in (s, t):       return bool if s == t else str
        elif float in (s, t):      return float
        else: return int
        
    @classmethod
    def _column_type(cls, vals):
        if non_string_iterable(vals):
            return reduce(lambda t,v: cls._merge_types(t, cls._column_type(v)), vals, type(None))
        else:
            return type(vals)
      
    @classmethod
    def load(cls, input, delimiter=',', type_annotations=True, array_separator='|', filter=None):
        reader = csv.reader(input, delimiter=delimiter)
        headings = next(reader)
        records = []
        for row in reader:
            d = {}
            for h,v in zip(headings, row):
                if v == '':
                    continue
                if type_annotations and isinstance(type_annotations, Mapping):
                    h = "{}_{}".format(h, type_annotations.get(h, "s"))
                if type_annotations and cls.TYPE_PATTERN.match(h):
                    h, array, typename = cls.TYPE_PATTERN.findall(h)[0]
                    vtype = cls.TYPE_ANNOTATIONS.get(typename, str)
                else: 
                    array, vtype = False, str
                if array:
                    d[h] = [cls._cast(vtype, v) for v in v.split(array_separator)]
                else:
                    d[h] = cls._cast(vtype, v)
            if not filter or filter(d):
                records.append(d)
        return records
    
    @classmethod
    def save(cls, output, records, delimiter=',', type_annotations=True, array_separator='|'):
        writer = csv.writer(output, delimiter=delimiter)
        headings = sorted(set(k for d in records for k in d.keys()))
        if type_annotations:
            is_array, col_type = {}, {}
            for h in headings:
                vals = [d.get(h, None) for d in records]
                is_array[h] = any(map(non_string_iterable, vals))
                col_type[h] = cls.TYPE_NAMES[cls._column_type(vals)]
            heading_row = ["{}_{}{}".format(h, 'a' if is_array[h] else '', col_type[h]) for h in headings]
        else:
            heading_row = headings
        writer.writerow(heading_row)
        for d in records:
            row = []
            for h in headings:
                v = d.get(h, '')
                if not type_annotations:
                    v = str(v)
                elif is_array[h] and non_string_iterable(v):
                    v = array_separator.join(str(x).replace(array_separator,'') for x in v)
                elif is_array[h]:
                    v = str(v).replace(array_separator,'')
                else:
                    v = str(v)
                row.append(v)
            writer.writerow(row)

class RecordSQLBase(object):
    """Abstract base class for records stored in a SQL backend. 
    WARNING: this performs no input sanitisation!"""
    
    @classmethod
    @ABC.abstractmethod
    def get_connection(cls, db_name):
        """Generate a connection from an implementation-specific db description."""
    
    @classmethod
    @ABC.abstractmethod
    def get_cursor(cls, connection):
        """Return a dict-like cursor."""

    @classmethod
    @ABC.abstractmethod
    def insert_parametrised(cls, table, params):
        """Return a parametrised insert statement."""
    
    @classmethod
    @ABC.abstractmethod
    def select_tables_query(cls, table_names):
        """Return a query for matching table names."""
    
    @classmethod
    def execute(cls, cursor, query, params=None):
        logger.debug("Executing SQL query: {}{}".format(query, "" if params is None else "\n\t{}".format(params)))
        cursor.execute(query, params) if params is not None else cursor.execute(query)
        
    @classmethod
    def tables_exist(cls, cursor, table_names):
        cls.execute(cursor, cls.select_tables_query(make_iterable(table_names)))
        return len(cursor.fetchall())
    
    @classmethod
    def _column_type(cls, vals):
        if all(isinstance(v, Integral) for v in vals): return "int"
        elif all(isinstance(v, Real) for v in vals): return "real"
        else: return "text"
    
    @classmethod
    def create_table(cls, cursor, table, rows, types, overwrite, indexes=()):
        exists = cls.tables_exist(cursor, table)
        if exists and overwrite:
            cls.execute(cursor, "DROP TABLE {name};".format(name=table))
        if not exists or overwrite:
            rows = ", ".join("{} {}".format(row, type) for row,type in zip(rows,types))
            cls.execute(cursor, "CREATE TABLE {name} ({rows});".format(name=table, rows=rows))
            for index in indexes:
                index_columns = make_iterable(index)
                index_name = "_".join(index_columns) + "_index"
                cls.execute(cursor, "CREATE INDEX {name} ON {table} ({columns});".format(name=index_name, table=table, columns=", ".join(index_columns)))
    
    @classmethod
    def save_records(cls, db_name, records, table, overwrite, indexes=(), array_annotations=True, array_separator='|'):
        """Save records to a table in a database."""
        logger.info("Saving records to SQL backend table {}".format(table))
        connection = cls.get_connection(db_name)
        cursor = cls.get_cursor(connection)
        headings = sorted(set(k for d in records for k in d.keys()))
        base_types = [cls._column_type([d.get(h, None) for d in records]) for h in headings]
        is_array = [array_annotations and any(non_string_iterable(d.get(h, None)) for d in records) for h in headings]
        annotated_headings = [h if not array else h + "_array" for (h,array) in zip(headings, is_array)]
        cls.create_table(cursor, table, annotated_headings, base_types, overwrite, indexes)
        for d in records:
            vals = tuple(d.get(h,'') for h in headings)
            vals = [array_separator.join(str(x).replace(array_separator, '') for x in make_iterable(v))
                    if array else str(v) if t == 'text' else v
                    for v,t,array in zip(vals, base_types, is_array)]
            sql = cls.insert_parametrised(table, vals)
            cls.execute(cursor, sql, vals)
        connection.commit()
        connection.close()
            
    @classmethod
    def load_records(cls, db_name, query, filter=None, array_annotations=True, array_separator='|'):
        """Load records from a database. The query can be either a table name or an arbitrary SELECT query."""
        if not query.upper().startswith("SELECT "):
            query = "SELECT * FROM {};".format(query)
        logger.info("Loading records using SQL query: {}".format(query))
        connection = cls.get_connection(db_name)
        cursor = cls.get_cursor(connection)
        cls.execute(cursor, query)
        records = []
        for row in cursor.fetchall():
            d = dict(zip(row.keys(), row))
            if array_annotations:
                d = dict((k, v) if not k.endswith("_array") else 
                         (k[:-len("_array")], v.split(array_separator))
                         for k,v in d.items())
            if not filter or filter(d):
                records.append(d)
        connection.close()
        return records

class RecordSQLite(RecordSQLBase):

    @classmethod
    def get_connection(cls, filename):
        connection = sqlite3.connect(filename)
        connection.row_factory = sqlite3.Row
        return connection
        
    @classmethod
    def get_cursor(cls, connection):
        return connection.cursor()

    @classmethod
    def insert_parametrised(cls, table, params):
        return "INSERT INTO {table} VALUES ({params});".format(table=table, params=",".join("?" for p in params))

    @classmethod
    def select_tables_query(cls, table_names):
        return "SELECT name FROM sqlite_master WHERE type='table' AND ({})".format(" OR ".join("name = '{}'".format(t) for t in table_names))

class RecordPostgreSQL(RecordSQLBase):

    @classmethod
    def get_connection(cls, connection_string):
        return psycopg2.connect(connection_string)
        
    @classmethod
    def get_cursor(cls, connection):
        return connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    @classmethod
    def insert_parametrised(cls, table, params):
        return "INSERT INTO {table} VALUES ({params});".format(table=table, params=",".join("%s" for p in params))

    @classmethod
    def select_tables_query(cls, table_names):
        return "SELECT tablename FROM pg_catalog.pg_tables WHERE {}".format(" OR ".join("name = '{}'".format(t) for t in table_names))
