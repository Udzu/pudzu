# [utils.py](utils.py)

## Summary 
Various utility functions and data structures.

## Dependencies
*Required*: [toolz](http://toolz.readthedocs.io/en/latest/index.html).
 
## Documentation

Selected examples below. For more, see the source.

### Classes

**optional_import**: optionally load a module.

```python
>> md = optional_import("module")
>> type(md)
utils.MissingModule
>> md.fn(1)
ImportError: Missing module: module
>> if md: md.fn(1)
>> md = optional_import("module", fn=str)
>> md.fn(1)
'1'
>> fn = optional_import_from("module", "fn", str)
>> fn(1)
'1'
```
  
**ValueCache**: a simple data container, allowing assignment in expressions.

```python
>> match = ValueCache()
>> if match.set(re.match(regex1, string)):
       foo(match.value.group(0))
   elif match.set(re.match(regex2, string)):    
       bar(match.value.group(1)
```

**CaseInsensitiveDict**: case-insensitive dictionary. Remembers the original case, and supports custom base dictionary containers such as OrderedDict and defaultdict.

```python
>> d = CaseInsensitiveDict({'Bob': 4098, 'Hope': 4139})
>> d
{'Hope': 4139, 'Bob': 4098}
>> d['BOB']
4098
>> d['bOb'] = 0
>> d
{'Hope': 4139, 'bOb': 0}

>> d = CaseInsensitiveDict(base_factory=OrderedDict)
>> d['Bob'] = 1
>> d['Hope'] = 2
>> d['BOB'] = 3
>> d
{'BOB': 3, 'Hope': 2}

>> d = CaseInsensitiveDict(base_factory=partial(defaultdict, lambda: 'Smith'))
>> d['Bob']
'Smith'
>> d['BOB']
'Smith'
>> d
{'Bob': 'Smith'}
```
    
### Decorators

**ignoring_extra_args**: wrapper that calls the function with the correct number of positional arguments and supported keyword arguments only. Useful for flexible user input.

```python
>> ignoring_extra_args(operator.eq)(4.99998, 5.0, 1e-5)
False
>> ignoring_extra_args(lambda x,y,n=0: abs(x-y)<=n)(4.99998, 5.0, 1e-3)
True
```

**ignoring_exceptions**: wrapper that catches exceptions and returns instead.

```python
>> ignoring_exceptions(requests.get, requests.exceptions.RequestException)(url)
```

**with_retries**: wrapper that retries a function when an exception is thrown.

```python
>> with_retries(request.get, max_retries=10, exceptions=ConnectionError)(url)
>> with_retries(request.get, max_duration=30, exceptions=ConnectionError)(url)
```

**cached_property**: decorator for cached properties that are calculated on first access and deleted after an optional timeout or on deletion. Useful for properties that are expensive to calculate.

```python
>> class Class():
       @cached_property
       def x(self):
           return random.random()
       @cached_property_expires_after(2)
       def y(self):
           return random.random()
>> obj = Class()
>> obj.x
0.6689880158698683
>> obj.x
0.6689880158698683
>> del obj.x
>> obj.x
0.536061023556316
>> obj.y
0.3697779198218838
>> sleep(3)
>> obj.y
0.05951785881072458
>> obj.y
0.05951785881072458
```
    
### Iterables

**non_string_iterable**: returns whether the input is an iterable other than string.

```python
>> non_string_iterable(itertools.count())
True
>> non_string_iterable("string")
False
```
    
**non_string_sequence**: returns whether the input is a sequence that is not a string (optionally with elements of a given type).

```python
>> non_string_sequence(range(10), int)
True
>> non_string_sequence(itertools.count())
False
```

**make_iterable**: returns an iterable, putting any non-iterable (or string) input in a tuple. Useful for flexible input arguments.

```python
>> make_iterable("123")
("123")
>> make_iterable(None)
()
>> make_iterable([1,2,3])
[1,2,3]
```

**remove_duplicates**: returns an order-preserving tuple copy of an iterable, deduplicated by a key.

```python
>> remove_duplicates("alabama")
('a', 'l', 'b', 'm')
>> remove_duplicates("she sells sea shells on the sea shore".split(" "), lambda s: s[0])
('she', 'on', 'the')
>> remove_duplicates("she sells sea shells on the sea shore".split(" "), lambda s: s[0], keep_last=True)
('on', 'the', 'shore')
```
    
**update_sequence**: returns a tuple copy of an iterable, with the nth element updated.

```python
>> update_sequence(range(4), 1, "bob")
(0, "bob", 2, 3)
```

**leafs**: generator returning all the non-string iterables inside an iterable.

```python
>> list(leafs([(1,[2],3),"four"]))
[1, 2, 3, 'four']
```

### Functions

**papply**: like functools.partial but also postpones evaluation of positional arguments with 
a value of Ellipsis (...).

```python
>> papply(print, ..., 2, ..., 4)(1, 3, 5)
1 2 3 4 5
```

**artial**: like functools.partial but also postpones evaluation of the first positional argument.

```python
>> artial(operator.lt, 2)(1)
True
```
