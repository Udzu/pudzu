import bisect
import datetime
import hashlib
import itertools
import logging
import math
import operator as op
import os.path
import random
import re
import unicodedata

from collections import abc, OrderedDict, Iterable, Mapping, Counter
from collections.abc import Sequence
from enum import Enum
from functools import wraps, partial
from importlib import import_module
from inspect import signature
from math import log10, floor, ceil
from time import sleep
from urllib.parse import urlparse

from toolz.dicttoolz import *
from toolz.functoolz import identity

# Configure logging

logging.basicConfig(format='[%(asctime)s] %(name)s:%(levelname)s - %(message)s', datefmt='%H:%M:%S', level=logging.INFO)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

# Classes

class MissingModule(object):
    """A class representing a missing module import: see optional_import."""
    def __init__(self, module, bindings):
        self._module = module
        for k,v in bindings.items():
            setattr(self, k, v)
    def __getattr__(self, k):
        raise ImportError("Missing module: {}".format(self._module))
    def __bool__(self):
        return False
    def __repr__(self):
        return "<MissingModule: {}>".format(self._module)
        
def optional_import(module, **bindings):
    """Optionally load the named module, returning a MissingModule
    object on failure, optionally with the given bindings."""
    try:
        return import_module(module)
    except ImportError:
        return MissingModule(module, bindings)
   
def optional_import_from(module, identifier, default=None):
    """Optionally import an identifier from the named module, returning the
    default value on failure."""
    return optional_import(module).__dict__.get(identifier, default)
    
class ValueCache():
    """A simple container with a returning assignment operator."""
    def __init__(self, value=None):
        self.value = value
    def __repr__(self):
        return "ValueCache({})".format(self.value)
    def set(self, value):
        self.value = value
        return value
    def __call__(self):
        return self.value
    def __lshift__(self, value):
        return self.set(value)
    def __rrshift__(self, value):
        return self.set(value)

# Decorators

def number_of_args(fn):
    """Return the number of positional arguments for a function, or None if the number is variable.
    Looks inside any decorated functions."""
    try:
        if hasattr(fn, '__wrapped__'):
            return number_of_args(fn.__wrapped__)
        if any(p.kind == p.VAR_POSITIONAL for p in signature(fn).parameters.values()):
            return None
        else:
            return sum(p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD) for p in signature(fn).parameters.values())
    except ValueError:
        # signatures don't work for built-in operators, so check for a few explicitly
        UNARY_OPS = [len, op.not_, op.truth, op.abs, op.index, op.inv, op.invert, op.neg, op.pos]
        BINARY_OPS = [op.lt, op.le, op.gt, op.ge, op.eq, op.ne, op.is_, op.is_not, op.add, op.and_, op.floordiv, op.lshift, op.mod, op.mul, op.or_, op.pow, op.rshift, op.sub, op.truediv, op.xor, op.concat, op.contains, op.countOf, op.delitem, op.getitem, op.indexOf]
        TERNARY_OPS = [op.setitem]
        if fn in UNARY_OPS:
            return 1
        elif fn in BINARY_OPS:
            return 2
        elif fn in TERNARY_OPS:
            return 3
        else:
            raise NotImplementedError("Bult-in operator {} not supported".format(fn))
      
def all_keyword_args(fn):
    """Return the names of all the keyword arguments for a function, or None if the number is variable.
    Looks inside any decorated functions."""
    try:
        if hasattr(fn, '__wrapped__'):
            return all_keyword_args(fn.__wrapped__)
        elif any(p.kind == p.VAR_KEYWORD for  p in signature(fn).parameters.values()):
            return None
        else:
            return [p.name for p in signature(fn).parameters.values() if p.kind in (p.KEYWORD_ONLY, p.POSITIONAL_OR_KEYWORD)]
    except ValueError:
        # signatures don't work for built-in operators, so check for a few explicitly, otherwise assume none
        BUILTINS = { }
        return BUILTINS.get(fn, [])
        
def ignoring_extra_args(fn):
    """Function decorator that calls the wrapped function with
    correct number of positional arguments, discarding any
    additional arguments."""
    n = number_of_args(fn)
    kwa = all_keyword_args(fn)
    @wraps(fn)
    def wrapper(*args, **kwargs):
        return fn(*args[0:n], **keyfilter(lambda k: kwa is None or k in kwa, kwargs))
    return wrapper

def ignoring_exceptions(fn, handler=None, exceptions=Exception):
    """Function decorator that catches exceptions, returning instead."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except exceptions:
            return handler(*args, **kwargs) if callable(handler) else handler
    return wrapper

def with_retries(fn, max_retries=None, max_duration=None, interval=0.5, exceptions=Exception):
    """Function decorator that retries the function when exceptions are raised."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if max_duration is None:
            end_time = datetime.datetime.max
        else:
            end_time = datetime.datetime.now() + datetime.timedelta(seconds=max_duration)
        for i in itertools.count() if max_retries is None else range(max_retries):
            try:
                return fn(*args, **kwargs)
            except exceptions:
                if i + 1 == max_retries: raise
                elif datetime.datetime.now() > datetime.datetime.max: raise
                else: sleep(interval)
    return wrapper

class cached_property(object):
    """Cached property decorator. Cache expires after a set interval or on deletion."""

    def __init__(self, fn, expires_after=None):
        self.__doc__ = fn.__doc__
        self.fn = fn
        self.name = fn.__name__
        self.expires_after = expires_after

    def __get__(self, obj, owner=None):
        if obj is None:
            return self
        if not hasattr(obj, '_property_cache_expiry_times'):
            obj._property_cache_expiry_times = {}
        if not hasattr(obj, '_property_cache_values'):
            obj._property_cache_values = {}
        if (obj._property_cache_expiry_times.get(self.name) is None or
            datetime.datetime.now() > obj._property_cache_expiry_times[self.name]):
            obj._property_cache_values[self.name] = self.fn(obj)
            if self.expires_after is None:
                obj._property_cache_expiry_times[self.name] = datetime.datetime.max
            else:
                obj._property_cache_expiry_times[self.name] = datetime.datetime.now() + datetime.timedelta(seconds=self.expires_after)
        return obj._property_cache_values[self.name]
            
    def __delete__(self, obj):
        if self.name in getattr(obj, '_property_cache_expiry_times', {}):
            del obj._property_cache_expiry_times[self.name]
        if self.name in getattr(obj, '_property_cache_values', {}):
            del obj._property_cache_values[self.name]
            
def cached_property_expires_after(expires_after):
    return partial(cached_property, expires_after=expires_after)

this = None
def with_vars(**kwargs):
    """Static variable decorator. Also binds (utils.)this to the function during execution."""
    def decorate(fn):
        for k, v in kwargs.items():
            setattr(fn, k, v)
        @wraps(fn)
        def wrapper(*args, **kwargs):
            global this
            oldthis, this = this, fn
            try:
                return fn(*args, **kwargs)
            finally:
                this = oldthis
        return wrapper
    return decorate

# Iterables
        
def non_string_iterable(v):
    """Return whether the object is any Iterable other than str."""
    return isinstance(v, Iterable) and not isinstance(v, str)

def make_iterable(v):
    """Return an iterable from an object, wrapping it in a tuple if needed."""
    return v if non_string_iterable(v) else () if v is None else (v,)

np = optional_import("numpy", ndarray=list)
def non_string_sequence(v, types=None):
    """Return whether the object is a Sequence other than str, optionally 
    with the given element types."""
    return (isinstance(v, Sequence) and not isinstance(v, str) or isinstance(v, np.ndarray)) and (types is None or all(any(isinstance(x, t) for t in make_iterable(types)) for x in v))

def make_sequence(v):
    """Return a sequence from an object, wrapping it in a tuple if needed."""
    return v if non_string_sequence(v) else () if v is None else (v,)
    
def unmake_sequence(v):
    """Return the first element of a sequence of length 1, otherwise leave unchanged."""
    return v[0] if non_string_sequence(v) and len(v) == 1 else v
        
def remove_duplicates(seq, key=lambda v:v, keep_last=False):
    """Return an order preserving tuple copy containing items from an iterable, deduplicated
    based on the given key function."""
    d = OrderedDict()
    for x in seq:
        k = key(x)
        if keep_last and k in d:
            del d[k]
        if keep_last or k not in d:
            d[k] = x
    return tuple(d.values())

def first(iterable, default=None):
    """Return the first element of an iterable, or a default if there aren't any."""
    try:
        return next(x for x in iter(iterable))
    except StopIteration:
        return default
    
def is_in(x, l):
    """Whether x is the same object as any member of l"""
    return any(x is y for y in l)

def update_sequence(s, n, x):
    """Return a tuple copy of s with the nth element replaced by x."""
    t = tuple(s)
    if -len(t) <= n < len(t):
        return t[0:n] + (x,) + t[n+1:0 if n ==-1 else None]
    else:
        raise IndexError("sequence index out of range")
        
def transpose_2d(array):
    """Transpose an array represented as an iterable of iterables."""
    return list(map(list, zip_equal(*array)))

def tmap(*args, **kwargs):
    """Like map, but returns a tuple."""
    return tuple(map(*args, **kwargs))
    
def tfilter(*args, **kwargs):
    """Like filter, but returns a tuple."""
    return tuple(filter(*args, **kwargs))
        
def treversed(*args, **kwargs):
    """Like reversed, but returns a tuple."""
    return tuple(reversed(*args, **kwargs))
    
def tmap_leafs(func, *iterables, base_factory=tuple):
    """Return a nested tuple (or other containers) containing the result of applying a function to the leaves of iterables of the same shape."""
    if not all(non_string_iterable(i) for i in iterables):
        return func(*iterables)
    elif non_string_sequence(base_factory):
        return base_factory[0](tmap_leafs(func, *subelts, base_factory=base_factory[1:]) for subelts in zip_equal(*iterables))
    else:
        return base_factory(tmap_leafs(func, *subelts, base_factory=base_factory) for subelts in zip_equal(*iterables))

# Generators

def zip_equal(*iterables, sentinel=object()):
    """Like zip, but throws an Exception if the arguments are of different lengths."""
    for i, subelts in enumerate(itertools.zip_longest(*iterables, fillvalue=sentinel)):
        if sentinel in subelts:
            raise ValueError('Iterables have different lengths (shortest is length {})'.format(i))
        yield subelts
    
def generate_leafs(iterable):
    """Generator that yields all the leaf nodes of an iterable."""
    if non_string_iterable(iterable):
        for x in iterable:
            yield from generate_leafs(x)
    else:
        yield iterable
            
def generate_batches(iterable, batch_size):
    """Generator that yields the elements of an iterable n at a time."""
    sourceiter = iter(iterable)
    while True:
        slice = list(itertools.islice(sourceiter, batch_size))
        if len(slice) == 0: break
        yield slice

def generate_ngrams(iterable, n):
    """Generator that yields n-grams from a iterable."""
    return zip(*[itertools.islice(it,i,None) for i,it in enumerate(itertools.tee(iterable, n))])

def repeat_each(iterable, repeats):
    """Generator that yields the elements of an iterable, repeated n times each."""
    return (p[0] for p in itertools.product(iterable, range(repeats)))

def filter_proportion(iterable, proportion):
    """Generator that yields 0 < proportion <= 1 of the elements of an iterable."""
    if not 0 < proportion <= 1:
        raise ValueError("Filter proportion must be between 0 and 1")
    sourceiter, p = iter(iterable), 0
    while True:
        v = next(sourceiter)
        p += proportion
        if p >= 1:
            p -= 1
            yield v

def generate_subsequences(iterable, start_if, end_if):
    """Generator that returns subsequences based on start and end condition functions. Both functions get passed the current element, while the end function optionally gets passed the current subsequence too."""
    sourceiter = iter(iterable)
    start = next(x for x in sourceiter if start_if(x))
    while True:
        x, subseq = next(sourceiter), [start]
        while not ignoring_extra_args(end_if)(x, subseq):
            subseq.append(x)
            x = next(sourceiter)
        yield subseq
        start = x if start_if(x) else next(x for x in sourceiter if start_if(x))

def riffle_shuffle(iterable, n=2):
    """Generator that performs a perfect riffle shuffle on the input, using a given number of subdecks."""
    return itertools.filterfalse(non, itertools.chain.from_iterable(zip(*list(itertools.zip_longest(*[iter(iterable)]*n)))))

# Mappings
    
def non(x):
    """Whether the object is None or a float nan."""
    return x is None or isinstance(x, float) and math.isnan(x)
    
def nnn(x):
    """Whether the object is neither None nor a float nan."""
    return not non(x)
    
def get_non(d, k, default=None):
    """Like get but treats None and nan as missing values."""
    v = d.get(k, default)
    return default if non(v) else v
    
def if_non(x, default):
    """Return a default if the value is None or nan."""
    return default if non(x) else x

def make_mapping(v, key_fn=identity):
    """Return a mapping from an object, using a function to generate keys if needed.
    Mappings are left as is, iterables are split into elements, everything else is
    wrapped in a singleton map."""
    if v is None: return {}
    elif isinstance(v, Mapping): return v
    elif non_string_iterable(v): return { ignoring_extra_args(key_fn)(i, x) : x for (i,x) in enumerate(v) }
    else: return { ignoring_extra_args(key_fn)(None, v) : v }

def merge_dicts(*dicts, merge_fn=lambda k, *vs: vs[-1], merge_all=False):
    """Merge a collection of dicts using the merge function, which is
    a function on conflicting field names and values."""
    def item_map(kv): return (kv[0], kv[1][0] if len(kv[1]) == 1 and not merge_all else merge_fn(kv[0], *kv[1]))
    return itemmap(item_map, merge_with(list, *dicts))

# Functions

def papply(func, *args, **kwargs):
    """Like functoools.partial, but also postpones evaluation of any positional arguments
    with a value of Ellipsis (...): e.g. papply(print, ..., 2, ..., 4)(1, 3, 5) prints 1 2 3 4 5."""
    min_args = sum(int(x is Ellipsis) for x in args)
    def newfunc(*fargs, **fkwargs):
        if len(fargs) < min_args:
            raise TypeError("Partial application expects at least {} positional arguments but {} were given".format(min_args, len(fargs)))
        newkwargs = kwargs.copy()
        newkwargs.update(fkwargs)
        newargs, i = [], 0
        for arg in args:
            if arg is Ellipsis:
                newargs.append(fargs[i])
                i += 1
            else:
                newargs.append(arg)
        newargs += fargs[i:]
        return func(*newargs, **newkwargs)
    return newfunc
    
def artial(func, *args, **kwargs):
    """Like functools.partial, but always omits the first positional argument."""
    def newfunc(*fargs, **fkwargs):
        if len(fargs) == 0:
            raise TypeError("Partial application expects at least 1 positional arguments but 0 were given")
        newkwargs = kwargs.copy()
        newkwargs.update(fkwargs)
        rargs = args + fargs[1:]
        return func(fargs[0], *rargs, **newkwargs)
    return newfunc

# Strings

def strip_from(str, *seps, last=False, ignore_case=False):
    """Strip everything from the first/last occurence of one of the seps."""
    flags = re.DOTALL | re.IGNORECASE * (ignore_case == True)
    regex = re.compile("(.*{greedy})({seps}).*".format(greedy="?"*(not last), seps="|".join(re.escape(sep) for sep in seps)), flags=flags)
    return re.sub(regex, r"\1", str)
    
def strip_after(str, *seps, last=False, ignore_case=False):
    """Strip everything after the first/last occurence of one of the seps."""
    flags = re.DOTALL | re.IGNORECASE * (ignore_case == True)
    regex = re.compile("(.*{greedy}({seps})).*".format(greedy="?"*(not last), seps="|".join(re.escape(sep) for sep in seps)), flags=flags)
    return re.sub(regex, r"\1", str)
    
def strip_to(str, *seps, last=False, ignore_case=False):
    """Strip everything to the first/last occurence of one of the seps."""
    flags = re.DOTALL | re.IGNORECASE * (ignore_case == True)
    regex = re.compile(".*{greedy}({seps})(.*)".format(greedy="?"*(not last), seps="|".join(re.escape(sep) for sep in seps)), flags=flags)
    return re.sub(regex, r"\2", str)
    
def strip_before(str, *seps, last=False, ignore_case=False):
    """Strip everything before the first/last occurence of one of the seps."""
    flags = re.DOTALL | re.IGNORECASE * (ignore_case == True)
    regex = re.compile(".*{greedy}(({seps}).*)".format(greedy="?"*(not last), seps="|".join(re.escape(sep) for sep in seps)), flags=flags)
    return re.sub(regex, r"\1", str)
    
def replace_any(str, substrings, new, count=0, ignore_case=False):
    """Replace any of substrings by new. New can be either a string or a function from matching string to string."""
    flags = re.DOTALL | re.IGNORECASE * (ignore_case == True)
    regex = re.compile("|".join(re.escape(old) for old in substrings), flags=flags)
    replacement = (lambda m: new(m.group(0))) if callable(new) else lambda m: new
    return re.sub(regex, replacement, str, count=count)
    
def strip_any(str, substrings, count=0, ignore_case=False):
    """Strip any of substrings."""
    return replace_any(str, substrings, "", count=count, ignore_case=ignore_case)

def replace_map(str, mapping, count=0, ignore_case=False):
    """Replace substrings using a mapping."""
    if ignore_case: mapping = CaseInsensitiveDict(mapping)
    return replace_any(str, mapping.keys(), lambda s: mapping[s], count=count, ignore_case=ignore_case)
    
def shortify(s, width, tail=5, placeholder='[...]', collapse_whitespace=True):
    """ Truncate a string to fit within a given width. A bit like textwrap.shorten."""
    if collapse_whitespace:
        s = re.sub("\s+", " ", s)
    if width < 2 * tail + len(placeholder):
        raise ValueError("Width parameter {} too short for tail={} and placeholder='{}'".format(width, tail, placeholder))
    elif len(s) <= width:
        return s
    else:
        return s[:width-tail-len(placeholder)] + placeholder + s[-tail:]

@with_vars(GERMAN_CONVERSIONS = { 'ß': 'ss', 'ẞ': 'SS', 'Ä': 'AE', 'ä': 'ae', 'Ö': 'OE', 'ö': 'oe', 'Ü': 'UE', 'ü': 'ue' },
           EXTRA_CONVERSIONS =  { 'ß': 'ss', 'ẞ': 'SS', 'Æ': 'AE', 'æ': 'ae', 'Œ': 'OE', 'œ': 'oe', 'Ĳ': 'IJ', 'ĳ': 'ij',
                                  'ﬀ': 'ff', 'ﬃ': 'ffi', 'ﬄ': 'ffl', 'ﬁ': 'fi', 'ﬂ': 'fl' })
def strip_accents(str, aggressive=False, german=False):
    """Strip accents from a string. Default behaviour is to use NFD normalization
    (canonical decomposition) and strip combining characters. Aggressive mode also
    replaces ß with ss, l with l, ø with o and so on. German mode replaces ö with oe, etc."""
    if german:
        def german_strip(c,d):
            c = this.GERMAN_CONVERSIONS.get(c, c)
            if len(c) > 1 and c[0].isupper() and d.islower(): c = c.title()
            return c
        str = "".join(german_strip(c,d) for c,d in generate_ngrams(str+" ", 2))
    str = "".join(c for c in unicodedata.normalize('NFD', str) if not unicodedata.combining(c))
    if aggressive:
        @partial(ignoring_exceptions, handler=identity, exceptions=KeyError)
        def aggressive_strip(c):
            if c in this.EXTRA_CONVERSIONS:
                return this.EXTRA_CONVERSIONS[c]
            name = unicodedata.name(c, '')
            variant = name.find(' WITH ')
            if variant: 
                return unicodedata.lookup(name[:variant])
            return c
        str = "".join(aggressive_strip(c) for c in str)
    return str
    
# Data structures

class KeyEquivalenceDict(abc.MutableMapping):
    """Mapping structure that views keys that normalize to the same thing as equivalent."""
    
    locals().update(Enum('KeyEquivalenceDict', 'USE_FIRST_KEY USE_LAST_KEY USE_NORMALIZED_KEY').__members__)
    
    def __init__(self, normalizer, d={}, base_factory=dict, key_choice=USE_LAST_KEY):
        self.normalizer = normalizer
        self.base_factory = base_factory
        self.key_choice = key_choice
        self._data = base_factory()
        self._keys = {}
        if isinstance(d, abc.Mapping):
            for k, v in d.items():
                self.__setitem__(k, v)
        elif isinstance(d, abc.Iterable):
            for (k, v) in d:
                self.__setitem__(k, v)
    
    def __getitem__(self, k):
        was_missing = self.normalizer(k) not in self._data
        v = self._data[self.normalizer(k)]
        if was_missing and self.normalizer(k) in self._data:
            # must be using a defaultdict of some kind
            self._keys[self.normalizer(k)] = k
        return v
    
    def __setitem__(self, k, v):
        self._data[self.normalizer(k)] = v
        if self.key_choice == KeyEquivalenceDict.USE_NORMALIZED_KEY:
            self._keys[self.normalizer(k)] = self.normalizer(k)
        elif self.key_choice == KeyEquivalenceDict.USE_LAST_KEY or self.normalizer(k) not in self._keys:
            self._keys[self.normalizer(k)] = k
        
    def __delitem__(self, k):
        del self._data[self.normalizer(k)]
        del self._keys[self.normalizer(k)]

    def __iter__(self):
        return (self._keys[k] for k in self._data)
        
    def __len__(self):
        return len(self._data)
        
    def __contains__(self, k):
        return self.normalizer(k) in self._data
        
    # repr and copy written to work with simple specialized subclasses
    def __repr__(self, normalizer=True, base_type=True, key_choice=True):
        return "{class_name}({{{elements}}}{normalizer}{base_type}{key_choice})".format(
            class_name = self.__class__.__name__, 
            elements = ", ".join("{!r}: {!r}".format(self._keys[k], v) for (k, v) in self._data.items()),
            normalizer = ", normalizer={}".format(self.normalizer.__name__) * bool(normalizer),
            base_type = ", base_type={}".format(type(self._data).__name__) * bool(base_type),
            key_choice = ", key_choice={}".format(self.key_choice) * bool(key_choice))
        
    def copy(self):
        copy = self.__class__.__new__(self.__class__)
        KeyEquivalenceDict.__init__(copy, self.normalizer, self, base_factory=self.base_factory, key_choice=self.key_choice)
        return copy
        
class CaseInsensitiveDict(KeyEquivalenceDict):
    """Case-insensitive mapping."""
    
    def __init__(self, d={}, base_factory=dict, key_choice=KeyEquivalenceDict.USE_LAST_KEY):
        super().__init__(str.lower, d, base_factory=base_factory, key_choice=key_choice)
        
    def __repr__(self):
        return super().__repr__(normalizer=False)
        
class ValueMappingDict(abc.MutableMapping):
    """Mapping structure that normalizes values before insertion using a function that gets passed the base dictionary, key and value. The function can either return the value to insert or throw a KeyError to skip insertion altogether."""
    
    def __init__(self, value_mapping, d={}, base_factory=dict):
        self.value_mapping = value_mapping
        self._data = base_factory()
        if isinstance(d, abc.Mapping):
            for k, v in d.items():
                self.__setitem__(k, v)
        elif isinstance(d, abc.Iterable):
            for (k, v) in d:
                self.__setitem__(k, v)
    
    def __getitem__(self, k):
        return self._data[k]
    
    def __setitem__(self, k, v):
        insert = True
        try:
            new_value = self.value_mapping(self._data, k, v)
        except KeyError:
            insert = False
        if insert:
            self._data[k] = new_value
        
    def __delitem__(self, k):
        del self._data[k]

    def __iter__(self):
        return (k for k in self._data)
        
    def __len__(self):
        return len(self._data)
        
    def __contains__(self, k):
        return k in self._data
        
    def __repr__(self):
        return "ValueMappingDict({{{}}}, value_mapping={}, base_type={})".format(", ".join("{!r}: {!r}".format(k, v) for (k, v) in self._data.items()), self.value_mapping.__name__, type(self._data).__name__)
        
# Numeric

def sign(x):
    """Sign indication of a number"""
    return 1 if x > 0 else -1 if x < 0 else 0
    
def round_significant(x, n=1):
    """Round x to n significant digits."""
    return 0 if x==0 else round(x, -int(floor(log10(abs(x)))) + (n-1))
    
def floor_digits(x, n=0):
    """Floor x to n decimal digits."""
    return floor(x * 10**n) / 10**n
    
def floor_significant(x, n=1):
    """Floor x to n significant digits."""
    return 0 if x==0 else floor_digits(x, -int(floor(log10(abs(x)))) + (n-1))

def ceil_digits(x, n=0):
    """Ceil x to n decimal digits."""
    return ceil(x * 10**n) / 10**n
    
def ceil_significant(x, n=1):
    """Ceil x to n significant digits."""
    return 0 if x==0 else ceil_digits(x, -int(floor(log10(abs(x)))) + (n-1))
    
def clip(x, low, high):
    """Clip x so that it lies between the low and high marks."""
    return max(low, min(x, high))
    
def format_float(x, p=None):
    """Format a float without unnecessary trailing 0s and with optional precision."""
    return "{:f}".format(x if p is None else round_significant(x,p)).rstrip('0').rstrip('.')

def weighted_choices(seq, weights, n):
    """Return random elements from a sequence, according to the given relative weights."""
    cum = list(itertools.accumulate(weights, op.add))
    return [seq[bisect.bisect_left(cum, random.uniform(0, cum[-1]))] for i in range(n)]

def weighted_choice(seq, weights):
    """Return a single random elements from a sequence, according to the given relative weights."""
    return weighted_choices(seq, weights, n=1)[0]

def _Counter_randoms(self, n, filter=None):
    """Return random elements from the Counter collection, weighted by count."""
    d = self if filter is None else { k : v for k,v in self.items() if filter(k) }
    return weighted_choices(list(d.keys()), list(d.values()), n=n)
    
def _Counter_random(self, filter=None):
    """Return a single random elements from the Counter collection, weighted by count."""
    return _Counter_randoms(self, 1, filter=filter)[0]
    
Counter.random_choices = _Counter_randoms
Counter.random_choice = _Counter_random

# Network/io

def printed(o, **kwargs):
    """Print an object and return it"""
    return print(o, **kwargs) or o

def url_to_filepath(url):
    """Convert url to a filepath of the form hostname/hash-of-path.extension. Ignores protocol, port, query and fragment."""
    uparse = urlparse(url)
    upath, uext = os.path.splitext(uparse.path)
    uname = hashlib.sha1(upath.encode('utf-8')).hexdigest()
    return os.path.join(uparse.netloc or "_local_", uname + uext)
   
