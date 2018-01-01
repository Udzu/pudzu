# [utils.py](utils.py)

## Summary 
Various utility functions and data structures.

## Dependencies
*Required*: [toolz](http://toolz.readthedocs.io/en/latest/index.html).
 
## Documentation

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
  
**ValueCache**: a simple data container, allowing assignment in expressions. Values can be assigned with <<, >> or .set, and extracted with () or .value.

```python
>> match = ValueCache()
>> if match << re.match(regex1, string):
       foo(match().group(0))
   elif match << re.match(regex2, string):
       bar(match().group(1)
```

**CaseInsensitiveDict**: case-insensitive dictionary. Remembers the original case, and supports custom base dictionary containers such as OrderedDict and defaultdict. Accepts a custom normalizer, so can be used for 'other'-insensitive dictionaries too.

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
>> ignoring_exceptions(operator.getitem)([], 0)
>> ignoring_exceptions(operator.truediv, exceptions=ZeroDivisionError, handler=lambda x,y: sign(x)*math.inf)(-4, 0)
-inf
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

**first_or_default**: return the first element of an iterable, or a default if there aren't any.

```python
>> first_or_default(count())
0
>> first_or_default([])
None
```

**is_in**: whether an object is object-identical to any member of an iterable

```python
>> x = []
>> is_in(x, [[]])
False
>> is_in(x, [[], x])
True
```

**update_sequence**: returns a tuple copy of an iterable, with the nth element updated.

```python
>> update_sequence(range(4), 1, "bob")
(0, "bob", 2, 3)
```

**tmap**, **tfilter**, **treversed**: like map, filter, reversed, but return tuples.

```python
>> tmap(str, (1, 2, 3))
('1', '2', '3')
```

### Generators

**generate_batches**: generator that yields items from an iterable n at a time.

```python
>> list(generate_batches(range(5), 3))
[[0, 1, 2], [3, 4]]
```

**generate_ngrams**: generator that yields n-grams from an iterable.

```python
>> list(generate_ngrams("ngram", 2))
[('n', 'g'), ('g', 'r'), ('r', 'a'), ('a', 'm')]
```

**generate_leafs**: generator that yields all the non-iterables (plus strings) inside an iterable.

```python
>> list(generate_leafs([(1,[2],3),"four"]))
[1, 2, 3, 'four']
```

**generate_subsequences**: generator that returns subsequences based on start and end condition functions. Both functions get passed the current element, while the end function optionally gets passed the current subsequence too.

```python
>>  list(islice(generate_subsequences(count(), lambda n: n % 2 == 0, lambda n: n % 3 == 0), 3))
[[0], [2, 3], [4, 5, 6]]
>> list(islice(generate_subsequences(count(), lambda n: n % 2 == 0, lambda _,l: len(l) == 3), 3))
[[0, 1, 2], [4, 5, 6], [8, 9, 10]]
```

**repeat_each**: generator that repeats each element in an iterable a certain number of times.

```python
>> list(repeat_each("ab", 3))
['a', 'a', 'a', 'b', 'b', 'b']
```

**filter_proportion**: generator that returns a certain proportion of an iterable's elements.

```python
>> list(filter_proportion(range(10), 1/3))
[2, 5, 8]
>> list(filter_proportion(range(10), 1/2))
[1, 3, 5, 7, 9]
```

**riffle_shuffle**: generator that performs a perfect riffle shuffle on the input, using a given number of subdecks.

```python
>> list(riffle_shuffle(range(10)))
[0, 2, 4, 6, 8, 1, 3, 5, 7, 9]
>> list(riffle_shuffle(range(10), 3))
[0, 3, 6, 9, 1, 4, 7, 2, 5, 8]
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

### Mappings

[TODO]

### Numeric

[TODO]