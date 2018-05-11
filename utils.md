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

**CaseInsensitiveDict**: case-insensitive dictionary. Remembers the original case, and supports custom base dictionary containers such as OrderedDict and defaultdict. Accepts a custom normalizer, so can be used for other key equivalences too (such as Unicode equivalence).

```python
>> d = CaseInsensitiveDict({'Bob': 4098, 'Hope': 4139})
>> d
CaseInsensitiveDict({'Hope': 4139, 'Bob': 4098}, base_type=dict)
>> d['BOB']
4098
>> del d['hope']
>> d['bOb'] = 0
>> d
CaseInsensitiveDict({'bOb': 0}, base_type=dict)

>> d = CaseInsensitiveDict(base_factory=OrderedDict)
>> d['Bob'] = 1
>> d['Hope'] = 2
>> d['BOB'] = 3
>> d
CaseInsensitiveDict({'BOB': 3, 'Hope': 2}, base_type=OrderedDict)

>> d = CaseInsensitiveDict(base_factory=partial(defaultdict, lambda: 'Smith'))
>> d['Bob']
'Smith'
>> d['BOB']
'Smith'
>> d
CaseInsensitiveDict({'Bob': 'Smith'}, base_type=defaultdict)
```

**NormalizingDict**: normalizing dictionary, using a function to convert or drop key-value pairs during assignment.

```python
>> d = NormalizingDict(lambda k,v: None if v == 0 else (k.upper(), abs(v)))
>> d["the"] = -1
>> d["rain"] = 0
>> d["spain"] = 2
>> d
NormalizingDict({'THE': 1, 'SPAIN': 2}, normalize=<lambda>, base_type=dict)
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

**non_string_iterable**: returns whether the input is an iterable other than a string.

```python
>> non_string_iterable(itertools.count())
True
>> non_string_iterable("string")
False
```
    
**non_string_sequence**: returns whether the input is a sequence other than a string (optionally with elements of a given type).

```python
>> non_string_sequence(range(10), int)
True
>> non_string_sequence(itertools.count())
False
```

**make_iterable**: returns an iterable, putting any non-string iterable input in a tuple. Useful for flexible input arguments. Similarly, **make_sequence**.

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

**transpose_2d**: returns a transposed list-of-lists copy of an iterable-of-iterables array.

```python
>> transpose_2d([[1,2],[3,4]])
[[1, 3], [2, 4]]
```

**tmap**, **tfilter**, **treversed**: like map, filter, reversed, but return tuples.

```python
>> tmap(str, (1, 2, 3))
('1', '2', '3')
```

**tmap_leafs**: applies a function to the non-string leafs inside iterables of the same shape, returning a nested tuple.

```python
>> tmap_leafs(op.add, [[1,2],3], [[4,5],6])
((5, 7), 9)
>> tmap_leafs(op.add, [[1,2],3], [[4,5],6], base_factory=list)
[[5, 7], 9]
>> tmap_leafs(op.abs, [[1,0,-1],-2], base_factory=(list, set))
[{0, 1}, 2]
```

### Generators

**zip_equal**: like zip, but throws an exception if the iterables have different lengths.

```python
>> list(zip_equal(range(2), [2,3]))
[(0, 2), (1, 3)]
>> list(zip_equal(range(5), itertools.count()))
ValueError: Iterables have different lengths (shortest is length 5)
```

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

**generate_leafs**: generator that yields all the non-string leafs inside an iterable.

```python
>> list(generate_leafs([(1,[2],3),"four"]))
[1, 2, 3, 'four']
```

**generate_subsequences**: generator that returns subsequences based on start and end condition functions. Both functions get passed the current element, while the end function optionally gets passed the current subsequence too.

```python
>>  list(islice(generate_subsequences(count(), lambda n: n % 2 == 0, lambda n: n % 3 == 0), 3))
[[0, 1, 2], [4, 5], [6, 7, 8]]
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

**make_mapping**: return a mapping from an object, using a function to generate keys if needed. Mappings are left as is, iterables are split into elements, everything else is wrapped in a singleton map.

```python
>> make_mapping(None)
{}
>> make_mapping("the")
{None: 'the'}
>> make_mapping(("rain", "in", "Spain"))
{0: 'rain', 1: 'in', 2: 'Spain'}
>> make_mapping({"stays": "mainly"})
{'stays': 'mainly'}
>> make_mapping(("on", "the", "plain"), key_fn=lambda i, v: len(v))
{2: 'on', 3: 'the', 5: 'plain'}
```

**merge_dicts**: merge a collection of dicts. Support a custom merge function, which is a function on conflicting key and values.

```python
>> merge_dicts({"a": 1, "b": 2}, {"a": 3, "c": 4}, {"c": 5})
{'a': 3, 'b': 2, 'c': 5}
>> merge_dicts({"a": 1, "b": 2}, {"a": 3, "c": 4}, {"c": 5}, merge_fn=lambda k, *vs: sum(vs))
{'a': 4, 'b': 2, 'c': 9}
```

### Strings

**strip_from**/**strip_to**/**strip_after**/**strip_before**: strip everything from/to/etc the first or last occurence of the given separators.

```python
>> text = "1. The rain in spain stays mainly on the plain"
>> strip_to(text, ". ")
'The rain in Spain stays mainly on the plain'
>> strip_after(text, "Spain", "Germany", ignore_case=True)
'1. The rain in spain'
>> strip_from(text, "he", last=True)
'1. The rain in spain stays mainly on t'
```

**replace_any**: replace any of a selection of substrings by new value, specified either as a constant string or a function from old string to new string. Similarly, **strip_any** strips any of the substrings, and **replace_map** replaces using a mapping of old to new.

```python
>> replace_any(text, "aeiou", "_")
'1. Th_ r__n _n sp__n st_ys m__nly _n th_ pl__n'
>> replace_any(text, "aeiou", "_", count=3)
'1. Th_ r__n in spain stays mainly on the plain'
>> replace_any(text, ["rain", "spain"], str.upper)
'1. The RAIN in SPAIN stays mainly on the plain'
>> replace_map(text, {"rain": "Spain", "Spain": "rain"}, ignore_case=True)
'1. The Spain in rain stays mainly on the plain'
>> strip_any(text, " .")
'1Theraininspainstaysmainlyontheplain'
```

### Numeric

**sign**: sign indication of a number.

```python
>> tmap(sign, (-4, 0, 10))
(-1, 0, 1)
```

**clip**: clip x so that it lies between the low and high marks.

```python
>> [clip(x, 1, 3) for x in (0, 3, 5)]
[1, 3, 3]
```

**floor_digits**/**ceil_digits**: floor or ceil a number to a given number of decimal places.

```python
>> floor_digits(1.573, 1)
1.5
>> ceil_digits(1.573, -1)
10.0
```

**round_significant**/**floor_significant**/**ceil_significant**: round, floor or ceil a number to a given number of significant figures.

```python
>> [round_significant(x, 2) for x in (1.573, 15.73, 1573)]
[1.6, 16.0, 1600]
```

**weighted_choice(s)**: return random element(s) from a sequence, according to the given relative weights.

```python
>>  weighted_choices(["H", "T"], [9, 1], 10)
['T', 'T', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H']
```

**Counter.random_choice(s)**: return random element(s) from a collection.Counter, weighted by count.

```python
>> Counter("HHHHHHHHHT").random_choices(10)
['H', 'H', 'H', 'H', 'H', 'H', 'H', 'T', 'H', 'H']
```