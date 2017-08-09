# [bamboo.py](bamboo.py)

## Summary 

A handful of utilities monkey-patched onto the pandas DataFrame class.

## Dependencies
*Required*: [pandas](http://pandas.pydata.org/), [toolz](http://toolz.readthedocs.io/en/latest/index.html), [utils](utils.md).

*Optional*: [pyparsing](http://pyparsing.wikispaces.com/) (for filter expressions).
 
## Documentation

### DataFrame

```python
>> df
   children   name     surname
0         2   Fred  Flintstone
1         2  Wilma  Flintstone
2        15   Dino         NaN
```

**filter_rows**: filter rows by a row predicate or a filter expression (see `FilterExpression` docstring for details).

```python
>> df.filter_rows(lambda r: r['name'] == "Fred")
   children  name     surname
0         2  Fred  Flintstone
>> df.filter_rows("name=Fred or children>2")
   children  name     surname
0         2  Fred  Flintstone
2        15  Dino         NaN
>> df.filter_rows("*name~stone") # field wildcard and regex match
   children   name     surname
0         2   Fred  Flintstone
1         2  Wilma  Flintstone
```

**filter_columns**: filter columns by column name, collection of names or name predicate.

```python
>> df.filter_columns('children')
   children
0         2
1         2
2        15
>> df.filter_columns(lambda c: 'name' in c)
    name     surname
0   Fred  Flintstone
1  Wilma  Flintstone
2   Dino         NaN
```

**assign_rows**: assign or update columns using a row function or constant, with an optional row predicate condition.

```python
>> df.assign_rows(assign_if="not surname:exists", pups=lambda r: r["children"], children=None)
   children   name     surname  pups
0       2.0   Fred  Flintstone   NaN
1       2.0  Wilma  Flintstone   NaN
2       NaN   Dino         NaN  15.0
>> df.assign_rows(assign_if="not surname:exists", surname=prompt_for_value(prompt=lambda r: r["name"]))
[Dino] = Snorkasaurus
   children   name       surname
0         2   Fred    Flintstone
1         2  Wilma    Flintstone
2        15   Dino  Snorkasaurus
```

**update_columns**: update existing columns using a value function or constant, with an optional value predicate condition.

```python
>> df.update_columns(update_if=True, surname=str.upper)
   children   name     surname
0         2   Fred  FLINTSTONE
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

**split_rows**: split rows by column, making one copy for each item in the column value.

```python
>> df.assign(children=[["Pebbles", "Stony"],["Pebbles", "Stony"], math.nan])
           children   name     surname
0  [Pebbles, Stony]   Fred  Flintstone
1  [Pebbles, Stony]  Wilma  Flintstone
2               NaN   Dino         NaN
>> _.split_rows("children")
  children   name     surname
0  Pebbles   Fred  Flintstone
1    Stony   Fred  Flintstone
2  Pebbles  Wilma  Flintstone
3    Stony  Wilma  Flintstone
4      NaN   Dino         NaN
```

**split_columns**: split column string values on a given delimiter.

```python
>> df.assign(children=["Pebbles,Stony","Pebbles,Stony", math.nan])
        children   name     surname
0  Pebbles,Stony   Fred  Flintstone
1  Pebbles,Stony  Wilma  Flintstone
2            NaN   Dino         NaN
>> _.split_columns(children)
           children   name     surname
0  (Pebbles, Stony)   Fred  Flintstone
1  (Pebbles, Stony)  Wilma  Flintstone
2                ()   Dino         NaN
```