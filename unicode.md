# [unicode.py](pudzu/sandbox/unicode/unicode.py)

## Summary 
Unicode data and manipulation.

## Dependencies
*Required*: [pandas](http://pandas.pydata.org/), [utils](utils.md).

## Documentation

**unicode_resources**: List the *.txt Unicode resource files present in the package (or a given path).

```python
>> unicode_resources()
['Blocks',
 'DerivedCoreProperties',
 'PropList',
 'ScriptExtensions',
 'Scripts',
 'UnicodeData',
 'emoji-data']
```
  
**unicode_data**: Extract the core unicode data and specified properties, either from the packaged files or from a given path. Extracts from fresh each time, so for repeat use it may make sense to save the result.

```python
>> unicode_data(("Blocks", "Scripts"))
[10:53:32] unicode:INFO - Extracting UnicodeData.txt from package...
[10:53:33] unicode:INFO - Extracting Blocks.txt from package...
[10:53:36] unicode:INFO - Extracting Scripts.txt from package...

                          Name General_Category  Canonical_Combining_Class  ... Code_Point                          Blocks    Scripts
0                    <control>               Cc                          0  ...       0000                     Basic Latin     Common
1                    <control>               Cc                          0  ...       0001                     Basic Latin     Common
2                    <control>               Cc                          0  ...       0002                     Basic Latin     Common
3                    <control>               Cc                          0  ...       0003                     Basic Latin     Common
4                    <control>               Cc                          0  ...       0004                     Basic Latin     Common
...                        ...              ...                        ...  ...        ...                             ...        ...
917995  VARIATION SELECTOR-252               Mn                          0  ...      e01eb  Variation Selectors Supplement  Inherited
917996  VARIATION SELECTOR-253               Mn                          0  ...      e01ec  Variation Selectors Supplement  Inherited
917997  VARIATION SELECTOR-254               Mn                          0  ...      e01ed  Variation Selectors Supplement  Inherited
917998  VARIATION SELECTOR-255               Mn                          0  ...      e01ee  Variation Selectors Supplement  Inherited
917999  VARIATION SELECTOR-256               Mn                          0  ...      e01ef  Variation Selectors Supplement  Inherited

[137994 rows x 15 columns]
```

## Data sources

Includes Unicode 12.1.0 data from https://www.unicode.org/Public/12.1.0/ucd/ and https://unicode.org/Public/emoji/12.1/. For terms of use, see http://www.unicode.org/terms_of_use.html.
