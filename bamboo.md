# [bamboo.py](pudzu/sandbox/bamboo.py)

## Summary 

A handful of utilities monkey-patched onto the pandas DataFrame class. Some were written before I properly understood pandas, and should be obsoleted.

## Dependencies
*Required*: [pandas](http://pandas.pydata.org/), [toolz](http://toolz.readthedocs.io/en/latest/index.html), [utils](utils.md).

*Optional*: [pyparsing](http://pyparsing.wikispaces.com/) (for filter expressions), [tqdm](https://pypi.org/project/tqdm/) (for progress bars).
 
## Documentation

```python
>> df
   children   name     surname
0         1   Fred  Flintstone
1         2  Wilma  Flintstone
2        15   Dino         NaN
```

### standalone functions

**pd_print**: print a value using the given pandas `display.` options (e.g. min_rows=60)

```python
>> pd_print(df, max_rows=2)
    children  name     surname
0          1  Fred  Filntstone
..       ...   ...         ...
2         15  Dino         NaN
```

### DataFrame

**filter_rows**: filter rows by a row/index predicate or a filter expression (see `FilterExpression` docstring for details). Less efficient than boolean indexing.

```python
>> df.filter_rows(lambda r: r['name'].startswith("F"))
   children  name     surname
0         2  Fred  Flintstone
>> df.filter_rows(lambda r, i: i % 2 == 0)
   children  name     surname
0         1  Fred  Flintstone
2        15   Dino         NaN
>> df.filter_rows("name=Fred or children>2")
   children  name     surname
0         1  Fred  Flintstone
2        15  Dino         NaN
>> df.filter_rows("*name~'^F'") # field wildcard and regex match
   children   name     surname
0         1   Fred  Flintstone
1         2  Wilma  Flintstone
```

**assign_rows**: assign or update columns using a row/index function or constant, with an optional row/index predicate condition. Supports progress bars using tqdm.

```python
>> df.assign_rows(assign_if="not surname:exists", pups=lambda r: r["children"], children=None)
   children   name     surname  pups
0       1.0   Fred  Flintstone   NaN
1       2.0  Wilma  Flintstone   NaN
2       NaN   Dino         NaN  15.0
>> df.assign_rows(assign_if="not surname:exists", surname=prompt_for_value(prompt=lambda r: r["name"]))
[Dino] = Snorkasaurus
   children   name       surname
0         1   Fred    Flintstone
1         2  Wilma    Flintstone
2        15   Dino  Snorkasaurus
```

**update_columns**: update existing columns using a value function or constant, with an optional value predicate condition. Supports progress bars using tqdm.

```python
>> df.update_columns(update_if=True, surname=str.upper)
   children   name     surname
0         1   Fred  FLINTSTONE
1         2  Wilma  FLINTSTONE
2        15   Dino         NaN
```

**groupby_rows**: group rows using a row function, map, list or column name.

```python
>> df.groupby_rows(lambda r: len(r['name'])).count()
   children  name  surname
4         2     2        1
5         1     1        1
```

**split_columns**: split column string values on a given delimiter.

```python
>> df.assign(children=["Pebbles","Pebbles,Stony", np.nan])
        children   name     surname
0        Pebbles   Fred  Flintstone
1  Pebbles,Stony  Wilma  Flintstone
2            NaN   Dino         NaN
>> _.split_columns("children", ",")
           children   name     surname
0         (Pebbles)   Fred  Flintstone
1  (Pebbles, Stony)  Wilma  Flintstone
2                ()   Dino         NaN
```

**explode_to_columns**: explode column sequence values to multiple columns.

```python
>> _.explode_to_columns("children")
           children   name     surname children_0 children_1
0        (Pebbles,)   Fred  Filntstone    Pebbles        NaN
1  (Pebbles, Stony)  Wilma  Flintstone    Pebbles      Stony
2                ()   Dino         NaN        NaN        NaN
```

**combine_columns**: combine columns into a tuple, ignoring NaNs and Nones, returning a series.

```python
>> _.combine_columns(["children_1", "children_0"])
0          (Pebbles,)
1    (Stony, Pebbles)
2                  ()
```
