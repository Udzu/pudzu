import bisect
import datetime
import hashlib
import importlib
import importlib.abc 
import importlib.util
import itertools
import logging
import math
import operator as op
import os.path
import random
import threading
import re
import sys
import types
import unicodedata

from collections import abc, OrderedDict, Counter
from collections.abc import Sequence, Iterable, Mapping
from enum import Enum
from functools import wraps, partial
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

# Imports

class MissingModule(types.ModuleType):
    def __getattr__(self, k):
        raise AttributeError(f"Missing module '{self.__name__}' has no attribute '{k}'")
    def __bool__(self):
        return False
    def __repr__(self):
        return f"<missing module '{self.__name__}'>"

def optional_import(name, **bindings):
    """Optionally import a module, returning a MissingModule with the given bindings on failure."""
    try:
        return importlib.import_module(name)
    except ImportError:
        m = MissingModule(name)
        for k,v in bindings.items():
            setattr(m, k, v)
        return m
   
def optional_import_from(module, identifier, default=None):
    """Optionally import an identifier from the named module, returning the
    default value on failure."""
    return optional_import(module).__dict__.get(identifier, default)

class OptionalModuleImporter(importlib.abc.PathEntryFinder, importlib.abc.Loader):

    SUFFIX = "_OPTIONAL"
    PATH_TRIGGER = "OptionalModuleImporterPathTrigger"
    
    def __init__(self, path):
        if path != self.PATH_TRIGGER:
            raise ImportError
    def find_spec(self, name, path=None, target=None):
        if name.endswith(self.SUFFIX):
            base = name[:-len(self.SUFFIX)]
            return importlib.util.find_spec(base) or importlib.util.spec_from_loader(base, self)
        return None
    def create_module(self, spec):
        return MissingModule(spec.name)
    def exec_module(self, module):
        pass

class AlternativeModuleImporter(importlib.abc.PathEntryFinder):

    INFIX = "_OR_"
    PATH_TRIGGER = "AlternativeModuleImporterPathTrigger"
    
    def __init__(self, path):
        if path != self.PATH_TRIGGER:
            raise ImportError
    def find_spec(self, name, path=None, target=None):
        if self.INFIX in name:
            first, second = name.split(self.INFIX, 1)
            return importlib.util.find_spec(first) or importlib.util.find_spec(second)
        return None

class VersionModuleImporter(importlib.abc.PathEntryFinder):

    REGEX = r"^(?P<base>.+)_V(?P<version>[0-9]+(?:_[0-9]+)*)$"
    PATH_TRIGGER = "VersionModuleImporterPathTrigger"

    def __init__(self, path):
        if path != self.PATH_TRIGGER:
            raise ImportError
    def find_spec(self, name, path=None, target=None):
        match = re.match(self.REGEX, name)
        if match:
            m = importlib.import_module(match["base"])
            if hasattr(m, '__version__'):
                expected_version = tuple(map(int, match["version"].split("_")))
                found_version = tuple(map(int, m.__version__.split(".")))
                if found_version[:len(expected_version)] >= expected_version:
                    return importlib.util.find_spec(match["base"])
        return None
            
def register_import_hooks():
    """Enable the import hooks in this file."""
    if OptionalModuleImporter not in sys.path_hooks:
        sys.path_hooks.append(OptionalModuleImporter)
        sys.path.append(OptionalModuleImporter.PATH_TRIGGER)
    if AlternativeModuleImporter not in sys.path_hooks:
        sys.path_hooks.append(AlternativeModuleImporter)
        sys.path.append(AlternativeModuleImporter.PATH_TRIGGER)
    if VersionModuleImporter not in sys.path_hooks:
        sys.path_hooks.append(VersionModuleImporter)
        sys.path.append(VersionModuleImporter.PATH_TRIGGER)

# Classes
    
class ValueBox(abc.Collection):
    """A simple mutable container with a returning assignment operator."""
    def __init__(self, value=None):
        self.value = value
    def __contains__(self, value):
        return value == self.value
    def __iter__(self):
        yield self.value
    def __len__(self):
        return 1
    def __repr__(self):
        return "ValueBox({})".format(self.value)
    def set(self, value):
        self.value = value
    def __call__(self):
        return self.value
    def __lshift__(self, value):
        self.set(value)
        return value
    def __rrshift__(self, value):
        self.set(value)
        return value

class ThreadLocalBox(threading.local, ValueBox):
    """A value box with thread-local storage."""
    def __repr__(self):
        return "ThreadLocalBox({})".format(self.value)
    
# Decorators

def number_of_positional_args(fn):
    """Return the number of positional arguments for a function, or None if the number is variable.
    Looks inside any decorated functions."""
    try:
        if hasattr(fn, '__wrapped__'):
            return number_of_positional_args(fn.__wrapped__)
        if any(p.kind == p.VAR_POSITIONAL for p in signature(fn).parameters.values()):
            return None
        else:
            return sum(p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD) for p in signature(fn).parameters.values())
    except ValueError:
        # signatures don't work for built-in operators, so try to extract from the docstring(!)
        if hasattr(fn, '__doc__') and hasattr(fn, '__name__') and fn.__doc__ is not None:
            specs = re.findall(r"{}\(.*?\)".format(re.escape(fn.__name__)), fn.__doc__)
            specs = [re.sub(r", \*, .*\)", ")", re.sub(r"[[\]]", "", spec)) for spec in specs]
            if any("*" in spec for spec in specs):
                return None
            elif specs:
                return max(0 if spec.endswith("()") else spec.count(",")+1 for spec in specs)
        raise NotImplementedError("Bult-in operator {} not supported".format(fn))
      
def names_of_keyword_args(fn):
    """Return the names of all the keyword arguments for a function, or None if the number is variable.
    Looks inside any decorated functions."""
    try:
        if hasattr(fn, '__wrapped__'):
            return names_of_keyword_args(fn.__wrapped__)
        elif any(p.kind == p.VAR_KEYWORD for  p in signature(fn).parameters.values()):
            return None
        else:
            return {p.name for p in signature(fn).parameters.values() if p.kind in (p.KEYWORD_ONLY, p.POSITIONAL_OR_KEYWORD)}
    except ValueError:
        # signatures don't work for built-in operators, so try to extract from the docstring(!)
        # only include optional arguments, since positional arguments are typically positional-only in built-ins
        if fn.__doc__ is not None:
            specs = re.findall(r"{}\(.*?\)".format(re.escape(fn.__name__)), fn.__doc__)
            if specs:
                return { arg for spec in specs for arg in re.findall(r"([^ ([]+)=", spec) }
        raise NotImplementedError("Bult-in operator {} not supported".format(fn))
        
def ignoring_extra_args(fn):
    """Function decorator that calls the wrapped function with
    correct number of positional arguments, discarding any
    additional arguments."""
    npa = number_of_positional_args(fn)
    kwa = names_of_keyword_args(fn)
    @wraps(fn)
    def wrapper(*args, **kwargs):
        return fn(*args[0:npa], **keyfilter(lambda k: kwa is None or k in kwa, kwargs))
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

def raise_exception(exception):
    """Raises an exception. For use in expressions."""
    raise exception
    
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
        self.expires_after = expires_after

    def __set_name__(self, owner, name):
        self.name = name
            
    def __get__(self, instance, owner):
        if instance is None:
            return self
        if not hasattr(instance, '_property_cache_expiration_times'):
            instance._property_cache_expiration_times = {}
        if not hasattr(instance, '_property_cache_values'):
            instance._property_cache_values = {}
        if (self.name not in instance._property_cache_expiration_times or
            datetime.datetime.now() > instance._property_cache_expiration_times[self.name]):
            instance._property_cache_values[self.name] = self.fn(instance)
            if self.expires_after is None:
                instance._property_cache_expiration_times[self.name] = datetime.datetime.max
            else:
                instance._property_cache_expiration_times[self.name] = datetime.datetime.now() + datetime.timedelta(seconds=self.expires_after)
        return instance._property_cache_values[self.name]
            
    def __delete__(self, instance):
        if self.name in getattr(instance, '_property_cache_expiration_times', {}):
            del instance._property_cache_expiration_times[self.name]
        if self.name in getattr(instance, '_property_cache_values', {}):
            del instance._property_cache_values[self.name]
            
def cached_property_expires_after(expires_after):
    return partial(cached_property, expires_after=expires_after)

this = ThreadLocalBox()
def with_vars(**kwargs):
    """Static variable decorator. Also binds utils.this() to the function during execution."""
    def decorate(fn):
        for k, v in kwargs.items():
            setattr(fn, k, v)
        @wraps(fn)
        def wrapper(*args, **kwargs):
            oldthis = this()
            this << fn
            try:
                return fn(*args, **kwargs)
            finally:
                this << oldthis
        return wrapper
    return decorate

# Iterables
        
def non_string_iterable(v):
    """Return whether the object is any Iterable other than str."""
    return isinstance(v, Iterable) and not isinstance(v, str)

def make_iterable(v):
    """Return an iterable from an object, wrapping it in a tuple if needed."""
    return v if non_string_iterable(v) else () if v is None else (v,)

def non_string_sequence(v, types=None):
    """Return whether the object is a Sequence other than str, optionally 
    with the given element types."""
    return (isinstance(v, Sequence) and not isinstance(v, str) or type(v).__name__ == 'ndarray') and (types is None or all(any(isinstance(x, t) for t in make_iterable(types)) for x in v))

def make_sequence(v):
    """Return a sequence from an object, wrapping it in a tuple if needed."""
    return v if non_string_sequence(v) else () if v is None else (v,)
    
def unmake_sequence(v):
    """Return None for an empty sequence, the first element of a sequence of length 1, otherwise leave unchanged."""
    if not non_string_sequence(v) or len(v) > 1: return v
    elif len(v) == 1: return v[0]
    else: return None
        
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
    try:
        start = next(x for x in sourceiter if start_if(x))
        while True:
            subseq = [start]
            try:
                x = next(sourceiter)
                while not ignoring_extra_args(end_if)(x, subseq):
                    subseq.append(x)
                    x = next(sourceiter)
            except StopIteration:
                yield subseq
                return
            yield subseq
            start = x if start_if(x) else next(x for x in sourceiter if start_if(x))
    except StopIteration:
        pass

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

def strip_accents(str, aggressive=False, german=False):
    """Strip accents from a string. Default behaviour is to use NFD normalization
    (canonical decomposition) and strip combining characters. Aggressive mode also
    replaces ß with ss, l with l, ø with o and so on. German mode first replaces ö
    with oe, etc."""
    if german:
        def german_strip(c, d, german_conversions={ 'ß': 'ss', 'ẞ': 'SS', 'Ä': 'AE', 'ä': 'ae',
                                                    'Ö': 'OE', 'ö': 'oe', 'Ü': 'UE', 'ü': 'ue' }):
            c = german_conversions.get(c, c)
            if len(c) > 1 and c[0].isupper() and d.islower(): c = c.title()
            return c
        str = "".join(german_strip(c,d) for c,d in generate_ngrams(str+" ", 2))
    str = "".join(c for c in unicodedata.normalize('NFD', str) if not unicodedata.combining(c))
    if aggressive:
        @partial(ignoring_exceptions, handler=identity, exceptions=KeyError)
        def aggressive_strip(c, extra_conversions={ 'ß': 'ss', 'ẞ': 'SS', 'Æ': 'AE', 'æ': 'ae',
                                                    'Œ': 'OE', 'œ': 'oe', 'Ĳ': 'IJ', 'ĳ': 'ij',
                                                    'ﬀ': 'ff', 'ﬃ': 'ffi', 'ﬄ': 'ffl', 'ﬁ': 'fi', 'ﬂ': 'fl' }):
            if c in extra_conversions:
                return extra_conversions[c]
            name = unicodedata.name(c, '')
            variant = name.find(' WITH ')
            if variant: 
                return unicodedata.lookup(name[:variant])
            return c
        str = "".join(aggressive_strip(c) for c in str)
    return str
    
def substitute(text, _pattern=r"\{\{(.*?)\}\}", **kwargs):
    """Format-style substitution but with arbitrary (but unescapable) patterns."""
    return re.sub(_pattern, lambda m: "{{{}}}".format(m.group(1)).format(**kwargs), text)

def indent_all_but_first(string, indent):
    """Indent all but the first line of a string."""
    return "\n".join(" "*indent*(i>0)+l for i,l in enumerate(string.split("\n")))

# Data structures

class KeyEquivalenceDict(abc.MutableMapping):
    """A dict-like object that views keys that normalize to the same thing
    as equivalent. Can be initialized from a mapping or iterable, like dict.
    Stores the underlying data in a base_factory(), and keeps track of
    the key specified by key_choice."""
    
    locals().update(Enum('KeyEquivalenceDict', 'USE_FIRST_KEY USE_LAST_KEY USE_NORMALIZED_KEY').__members__)
    
    def __init__(self, data={}, normalizer=identity, base_factory=dict, key_choice=USE_LAST_KEY):
        self.normalizer = getattr(self, "default_normalizer", normalizer)
        self.base_factory = getattr(self, "default_base_factory", base_factory) 
        self.key_choice = getattr(self, "default_key_choice", key_choice) 
        if not isinstance(key_choice, type(self.USE_LAST_KEY)):
            raise TypeError(f"Invalid key_choice parameter {key_choice!r}")
            
        self._data = base_factory()
        self._keys = {}
        if isinstance(data, abc.Mapping):
            for k, v in data.items():
                self.__setitem__(k, v)
        elif isinstance(data, abc.Iterable):
            for (k, v) in data:
                self.__setitem__(k, v)
        else:
            raise TypeError(f"'{type(data).__name__}' object is not iterable")
    
    # abc methods
    def _update_keymap(self, nk, k, update_if_present=False):
        if nk in self._data and (nk not in self._keys or update_if_present):
            self._keys[nk] = nk if self.key_choice == KeyEquivalenceDict.USE_NORMALIZED_KEY else k
        elif nk not in self._data and nk in self._keys:
            del self._keys[nk]
    
    def __setitem__(self, k, v):
        nk = self.normalizer(k)
        self._data[nk] = v
        self._update_keymap(nk, k, self.key_choice == KeyEquivalenceDict.USE_LAST_KEY)
        
    def __getitem__(self, k):
        nk = self.normalizer(k)
        v = self._data[nk]
        self._update_keymap(nk, k)
        return v
    
    def __delitem__(self, k):
        nk = self.normalizer(k)
        del self._data[nk]
        self._update_keymap(nk, k)

    def __iter__(self):
        return (self._keys[k] for k in self._data)
        
    def __len__(self):
        return len(self._data)
        
    # mixin overrides
    def __contains__(self, k):
        return self.normalizer(k) in self._data
        
    def __eq__(self, other):
        if not isinstance(other, abc.Mapping):
            return NotImplemented
        if len(self) != len(other):
            return False
        for k,v in other.items():
            if k not in self or self[k] != v:
                return False
        return True
    
    # handle specialized subclasses
    def __init_subclass__(cls, normalizer=None, base_factory=None, key_choice=None, **kwargs):
        if normalizer: cls.default_normalizer = staticmethod(normalizer)
        if base_factory: cls.default_base_factory = staticmethod(base_factory)
        if key_choice: cls.default_key_choice = key_choice
        super().__init_subclass__(**kwargs)
        
    def __repr__(self):
        return "{class_name}({{{elements}}}{normalizer}{base_type}{key_choice})".format(
            class_name = self.__class__.__name__, 
            elements = ", ".join("{!r}: {!r}".format(self._keys[k], v) for (k, v) in self._data.items()),
            normalizer = ", normalizer={}".format(self.normalizer.__name__) * (not hasattr(self, "default_normalizer")),
            base_type = ", base_type={}".format(type(self._data).__name__) * (not hasattr(self, "default_base_factory")),
            key_choice = ", key_choice={}".format(self.key_choice) * (not hasattr(self, "default_key_choice")))
        
    def __copy__(self):
        copy = self.__class__.__new__(self.__class__)
        KeyEquivalenceDict.__init__(copy, self, normalizer=self.normalizer, base_factory=self.base_factory, key_choice=self.key_choice)
        return copy
        
    def copy(self):
        return self.__copy__()
        
class CaseInsensitiveDict(KeyEquivalenceDict, normalizer=str.lower):
    """A case-insensitive dict-like object. Can be initialized from a mapping or iterable,
    like dict. Stores the underlying data in a base_factory(), and keeps track of
    the key specified by key_choice."""
    
    def __init__(self, data={}, base_factory=dict, key_choice=KeyEquivalenceDict.USE_LAST_KEY):
        super().__init__(data, base_factory=base_factory, key_choice=key_choice)
        
class ValueMappingDict(abc.MutableMapping):
    """Mapping structure that normalizes values before insertion using a function that gets
    passed the base dictionary, key and value. The function can either return the value to
    insert or throw a ValueMappingDict.SkipInsertion to skip insertion altogether."""
    
    class SkipInsertion(Exception):
        pass
    
    def __init__(self, data={}, value_mapping=identity, base_factory=dict):
        self.value_mapping = getattr(self, "default_value_mapping", value_mapping)
        self.base_factory = getattr(self, "default_base_factory", base_factory)
        self._data = base_factory()
        if isinstance(data, abc.Mapping):
            for k, v in data.items():
                self.__setitem__(k, v)
        elif isinstance(data, abc.Iterable):
            for (k, v) in data:
                self.__setitem__(k, v)
        else:
            raise TypeError("'{}' object is not iterable".format(type(data).__name__))
    
    def __setitem__(self, k, v):
        try:
            self._data[k] = self.value_mapping(self._data, k, v)
        except self.SkipInsertion:
            pass
        
    def __getitem__(self, k): return self._data[k]
    def __delitem__(self, k): del self._data[k]
    def __iter__(self): return (k for k in self._data)
    def __len__(self): return len(self._data)
    def __contains__(self, k): return k in self._data
        
    # handle specialized subclasses
    def __init_subclass__(cls, value_mapping=None, base_factory=None, **kwargs):
        if value_mapping: cls.default_value_mapping = staticmethod(value_mapping)
        if base_type: cls.default_base_factory = staticmethod(base_factory)
        super().__init_subclass__(**kwargs)
        
    def __repr__(self):
        return "{class_name}({{{elements}}}{value_mapping}{base_type})".format(
            class_name = self.__class__.__name__, 
            elements = ", ".join("{!r}: {!r}".format(k, v) for (k, v) in self._data.items()),
            value_mapping = ", value_mapping={}".format(self.value_mapping.__name__) * (not hasattr(self, "default_value_mapping")),
            base_type = ", base_type={}".format(type(self._data).__name__) * (not hasattr(self, "default_base_factory")))
        
    def __copy__(self):
        copy = self.__class__.__new__(self.__class__)
        ValueMappingDict.__init__(copy, self, value_mapping=self.value_mapping, base_factory=self.base_factory)
        return copy
        
    def copy(self):
        return self.__copy__()

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
   
# Parameterization

def parameterized_class(globals, class_suffixes=None, **kwargs):
    """Decorator for generating parameterized classes. To use, pass in the calling
    module's globals(), parallel lists of named parameterized values, and optional class
    name suffixes. This will generate appropriately named classes for each value
    combination, with the parameters available in the base class as class attributes."""
    def decorator(cls):
        suffixes = class_suffixes or itertools.repeat(None)
        for psuffix, pvalues in zip(suffixes, zip(*list(kwargs.values()))):
            params = { k : v for k,v in zip(kwargs.keys(), pvalues) }
            suffix = psuffix or ''.join(str(p).title() for p in pvalues)
            globals[cls.__name__+suffix] = type(cls.__name__+suffix, (cls,), params)
            if cls.__doc__:
                globals[cls.__name__+suffix].__doc__ = cls.__doc__ + \
                    " [{suffix}{values}]".format(
                       suffix = "{}: ".format(psuffix) if psuffix else "",
                       values = ", ".join("{}={}".format(k, shortify(str(p), 40)) for k,p in params.items()))
        return None
    return decorator
    
def parameterized_method(method_suffixes=None, **kwargs):
    """Decorator for generating parameterized class methods. To use, use the
    MetaParameterized metclass, and decorate the methods, passing in parallel lists
    of named parameterized vaues, and optional method name suffixes. This will generate
    appropriately named methods for each value combination, with the parameters
    passed into the base method as named arguments."""
    def decorator(func):
        func._parameterized_kwargs = kwargs
        func._parameterized_suffixes = method_suffixes
        return func
    return decorator
    
class MetaParameterized(type):
    """Metaclass to support parameterized class methods, decorated with @parameterized_method."""
    def __new__(metacls, name, bases, attrs):
        for (n,fn) in [(n,fn) for (n,fn) in attrs.items() if hasattr(fn, '_parameterized_kwargs')]:
            kwargs = fn._parameterized_kwargs
            suffixes = fn._parameterized_suffixes or itertools.repeat(None)
            for psuffix, pvalues in zip(suffixes, zip(*list(kwargs.values()))):
                params = { k : v for k,v in zip(kwargs.keys(), pvalues) }
                suffix = psuffix or ''.join('_{}'.format(p) for p in pvalues)
                def make_parameterized_fn(fn, params):
                    def parameterized_fn(self, *args, **kwargs):
                        kwargs.update(params)
                        return fn(self, *args, **kwargs)
                    return parameterized_fn
                attrs[n+suffix] = make_parameterized_fn(fn, params)
                if fn.__doc__:
                    attrs[n+suffix].__doc__ = fn.__doc__ + \
                        " [{suffix}{values}]".format(
                           suffix = "{}: ".format(psuffix) if psuffix else "",
                           values = ", ".join("{}={}".format(k, shortify(str(p), 40)) for k,p in params.items()))
            del attrs[n] 
        return type.__new__(metacls, name, bases, attrs)

# Switch statements (because why not)

class switch():
    """A context manager for emulating switch statements.
    
    with switch(x) as s:
        s.case(0) << "zero"
        s.case(1, 2) << "one or two"
        @s.case(3)
        def _():
            print("print something")
            return "three"
        s.default << "something else"
    print(s.return_value)
    """

    def __init__(self, obj, predicates=False, police_enums=True):
        self.obj = obj
        self.predicates = predicates 
        self.police_enums = police_enums
        
    def __enter__(self):
        self.case = self.Case()
        self.default = self.Default()
        return self

    class Case():

        def __init__(self):
            self.dispatch = ValueMappingDict(lambda d,k,v: raise_exception(KeyError("Key {} already present in switch statement".format(k))) if k in d else v, base_factory=OrderedDict)
            
        def __call__(self, *args):
            return self.CaseVal(self.dispatch, *args)

        class CaseVal():
            def __init__(self, dispatch, *args):
                self.dispatch = dispatch
                self.args = args
                
            def __lshift__(self, val):
                self.dispatch.update((a, (lambda: val)) for a in self.args)
                
            def __call__(self, fn):
                self.dispatch.update((a, fn) for a in self.args)
                
    class Default():
    
        def _set_default(self, val):
            if hasattr(self, 'default'):
                assert KeyError("Default case already present in switch statement")
            self.default = val
        
        def __lshift__(self, val):
            self._set_default(lambda: val)
            
        def __call__(self, fn):
            self._set_default(fn)
            
    def __exit__(self, exc_type, exc_value, traceback):
    
        if exc_type is not None:
            return
            
        if self.police_enums and not hasattr(self.default, 'default'):
            enum_types = { type(x) for x in ({ self.obj } if self.predicates else self.case.dispatch) if isinstance(x, Enum) }
            for enum_type in enum_types:
                missing = [ e for e in enum_type if not (any(p(e) for p in self.case.dispatch) if self.predicates else e in self.case.dispatch) ]
                if missing:
                    raise KeyError("Incomplete switch handling for {}: missing {} (set police_enums=False to ignore)".format(enum_type, ", ".join(map(str, missing))))
                    
        try:
            return_proc = next(v for p,v in self.case.dispatch.items() if p(self.obj)) \
                          if self.predicates else self.case.dispatch[self.obj]
        except (KeyError, StopIteration):
            if not hasattr(self.default, 'default'):
                raise KeyError("No switch handling for {}".format(self.obj))
            return_proc = self.default.default
        self.return_value = return_proc()
            
switch_predicates = partial(switch, predicates=True)
