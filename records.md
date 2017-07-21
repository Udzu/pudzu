# [records.py](records.py)

## Summary 
Various utilities for handling records (lists of dicts), grouped records (ordered dicts of records) and tables (pandas dataframes). Fairly lightweight with an emphasis on pure functional manipulation of builtin structures. Some overlap with packages such as pandas; this is certainly not the only (or necessarily best) way to handle records, but should have a reasonably shallow learning curve. Not optimised for speed.

## Dependencies
*Required*: [toolz](http://toolz.readthedocs.io/en/latest/index.html), [utils](utils.md).

*Optional*: [pyparsing](http://pyparsing.wikispaces.com/) (for filter expressions), [pandas](http://pandas.pydata.org/) (for tabulation), [tqdm](https://pypi.python.org/pypi/tqdm) (for progress bars), [psycopg2](http://initd.org/psycopg/) (for postgres backend).
 
## Documentation

### Records

Records are just lists of dicts, usually with the same or overlapping keys. Records can be used to initialise pandas dataframes by `pd.DataFrame(rs)` and can be extracted by `df.to_dict('records')`.

```python
>> rs = [ { "name": "Fred", "surname": "Flintstone", "children": 2 },
          { "name": "Wilma", "surname": "Flintstone", "children": 2 },
          { "name": "Dino", "children": 15 } ]
>> record_keys(rs)
['name', 'children', 'surname']
>> record_values(rs, 'name')
['Fred', 'Wilma', 'Dino']
>> record_values(rs, 'surname')
['Flintstone']
>> pd.DateFrame(rs)
   children   name     surname
0         2   Fred  Flintstone
1         2  Wilma  Flintstone
2        15   Dino         NaN
```

Records can be filtered using functions or filter expressions (see `RecordFilter` docstring for details).

```python
>> filter_records(rs, lambda d: d.get("name") == "Fred")
[{'children': 2, 'name': 'Fred', 'surname': 'Flintstone'}]
>> filter_records(rs, "name=Fred")
[{'children': 2, 'name': 'Fred', 'surname': 'Flintstone'}]
>> filter_records(rs, "name=Fred or children>2")
[{'children': 2, 'name': 'Fred', 'surname': 'Flintstone'},
 {'children': 15, 'name': 'Dino'}]
>> filter_records(rs, "*name~stone") # field wildcard and regex match
[{'children': 2, 'name': 'Fred', 'surname': 'Flintstone'},
 {'children': 2, 'name': 'Wilma', 'surname': 'Flintstone'}]
``` 

Keys can also be filtered:

```python
>> filter_records(rs, "surname=Flintstone", key_filter=['name', 'children'])
[{'children': 2, 'name': 'Fred'},
 {'children': 2, 'name': 'Wilma'}]
>> filter_records(rs, key_filter=lambda k: 'name' in k)
[{'name': 'Fred', 'surname': 'Flintstone'},
 {'name': 'Wilma', 'surname': 'Flintstone'},
 {'name': 'Dino'}]
```

Records can be updated functionally using `update_record` and the related helper functions.

```python
>> update_records(rs, len)
[3, 3, 2]
>> mark_person = update_if("surname:exists", update_with(person=lambda d: True))
>> mark_full_name = update_with(fullname=lambda d:" ".join(d[x] for x in ['name', 'surname'] if x in d))
>> mark_pups = update_if("not person:true", update_with(children=lambda d:None, pups=lambda d:d['children']))
>> update_records(rs, update_all(mark_person, mark_full_name, mark_pups))
[{'children': 2,
  'fullname': 'Fred Flintstone',
  'name': 'Fred',
  'person': True,
  'surname': 'Flintstone'},
 {'children': 2,
  'fullname': 'Wilma Flintstone',
  'name': 'Wilma',
  'person': True,
  'surname': 'Flintstone'},
 {'fullname': 'Dino', 'name': 'Dino', 'pups': 15}]
>> rs = update_records(rs, update_if("not surname:exists", prompt_for_value('surname',prompt=lambda d:d['name'])))
[Dino] = Snorkasaurus
>> rs
[{'children': 2, 'name': 'Fred', 'surname': 'Flintstone'},
 {'children': 2, 'name': 'Wilma', 'surname': 'Flintstone'},
 {'children': 15, 'name': 'Dino', 'surname': 'Snorkasaurus'}]
```

Records can be merged with `merge_records`.

### Grouped records

Grouped records are just OrderedDicts, mapping group names to records. They can be created using `group_records`, which is bears some similarities to the pandas groupby method:

```python
>> group_records(rs, "surname")
OrderedDict([('Flintstone',
              [{'children': 2, 'name': 'Fred', 'surname': 'Flintstone'},
               {'children': 2, 'name': 'Wilma', 'surname': 'Flintstone'}]),
             ('Snorkasaurus',
              [{'children': 15, 'name': 'Dino', 'surname': 'Snorkasaurus'}])])
>> group_records(rs, lambda d: len(d['name']), groups=range(4,7))
OrderedDict([(4,
              [{'children': 2, 'name': 'Fred', 'surname': 'Flinstone'},
               {'children': 15, 'name': 'Dino', 'surname': 'Snorkasaurus'}]),
             (5, [{'children': 2, 'name': 'Wilma', 'surname': 'Flinstone'}]),
             (6, [])])
>> group_records(rs, lambda d: list(d['name']), groups=list("iou"))
OrderedDict([('i',
              [{'children': 2, 'name': 'Wilma', 'surname': 'Flintstone'},
               {'children': 15, 'name': 'Dino', 'surname': 'Snorkasaurus'}]),
             ('o',
              [{'children': 15, 'name': 'Dino', 'surname': 'Snorkasaurus'}]),
             ('u', [])])
>> group_records(rs, lambda d, g: g[0] <= d['children'] <= g[1], groups=((1,10),(11,20)), by_filter=True)
OrderedDict([((1, 10),
              [{'children': 2, 'name': 'Fred', 'surname': 'Flintstone'},
               {'children': 2, 'name': 'Wilma', 'surname': 'Flintstone'}]),
             ((11, 20),
              [{'children': 15, 'name': 'Dino', 'surname': 'Snorkasaurus'}])])
```

Groups can be filtered with `filter_groups`, sorted with `sorted_groups`, updated with `update_groups` and merged with `merge_groups`.

### Tables

Tables are just pandas dataframes, with row and column labels. They can be generated from records with `tabulate_records` or group maps with `tabulate_groups`. Both use `group_records` under the covers (and could probably be simplified).

```python
>> tabulate_records(rs, row_group_by="name", col_group_by="surname", fn=len)
       Flintstone  Snorkasaurus
Fred            1             0
Wilma           1             0
Dino            0             1
>> tabulate_records(rs, rows=((1,5),(6,10),(11,15)), columns=("name", "surname"),
                    col_group_by=lambda d,col,row: row[0]<=len(d[col])<=row[1], col_filter=True,
                    fn=len)
          name  surname
(1, 5)       3        0
(6, 10)      0        2
(11, 15)     0        1
```
    
### Serialisation

There are also a number of classes for saving and loading records. Supported formats include: CSV, JSON, SQLite and PostgreSQL. Unlike in pandas, there is no automatic type detection on loading, but CSV and SQL serialisation supports basic type annotation in row titles. For more details, see docstrings.

```python
>> RecordCSV.save_file("flintstones.csv", rs)
[10:02:05] records:INFO - Saving to .\flintstones.csv
>> RecordCSV.save_files("flintstones_.csv", group_records(rs, "surname"))
[10:02:07] records:INFO - Saving to .\flintstones_Flintstone.csv
[10:02:07] records:INFO - Saving to .\flintstones_Snorkasaurus.csv
>> rs = RecordCSV.load_file("futurama.csv", delimiter='\t', encoding='latin-1')
[10:02:10] records:INFO - Loading from futurama.csv
```
  
