# [nounce.py](nounce.py)

## Summary 
Simple IPA-based pronouncing and rhyming dictionary. 

## Dependencies
*Required*: [toolz](http://toolz.readthedocs.io/en/latest/index.html), [utils](utils.md).

## Documentation

### Nouncer

A simple pronouncing dictionary that supports IPA input and output, as well as importing from CMU dict and pronunciation lists.

```python
>> pdict = Nouncer()
>> pdict.import_cmudict("cmudict.0.7a")
>> pdict
<Nouncer: 123691 entries>
>> pdict["polish"]
{'pˈoʊlɪʃ', 'pˈɑlɪʃ'}
>> pdict["polish"] = 'ˈpɒlɪʃ'
>> pdict["polish"]
{'pˈoʊlɪʃ', 'pˈɑlɪʃ', 'pˈɒlɪʃ'}
>> pdict["polish"] = {'ˈpɒlɪʃ'}
>> pdict["polish"]
{'pˈɒlɪʃ'}
>> del pdict["polish"]
>> pdict.save("unpolished")
>> pdict = Nouncer("unpolished")
```


**pronunciations**: generator returning individual pronunciations. Supports function or regex filters.

```python
>> next(pdict.pronunciations(word_filter="^k", pronunciation_filter="^[^k]"))
('kneller', 'nˈɛlɝ')
>> next(pdict.pronunciations(word_filter=lambda w: len(w) > 15))
("representative's", 'rˌɛprɪzˈɛnətɪvz')
```

**syllables**: number of syllables for a given word. Supports a syllable counter for missing words. A simple heuristic implementation for English is provided in **english_syllables**, though this is only around 90% accurate.

```python
>> pdict.syllables("resume")
{'rizˈum': 2, 'rɪzˈum': 2, 'rˈɛzəmˌeɪ': 3}
>> pdict.syllables("wugging", english_syllables)
{'(wugging)': 2}
```

**rhymes**: words that rhyme with a given word. Options include identirhyme (allow the same consonant before the stress: e.g. head/behead), multirhyme (allow arbitrary internal consonants: e.g. beheading/depressing) and enjambment (return truncated rhymes: e.g. beheading/bread).

```python
>> pdict.rhymes("inconceivable")
{'ˌɪnkənsˈivəbəl': ['unbelievable', 'believable', 'achievable']}
>> pdict.rhymes("inconceivable", identirhyme=True)
{'ˌɪnkənsˈivəbəl': ['inconceivable', 'receivable', 'unbelievable', 'believable', 'achievable', 'conceivable']}
>> pdict.rhymes("inconceivable", multirhyme=True)
{'ˌɪnkənsˈivəbəl': ['learonal', 'impeachable', 'amenable', 'unreasonable', ... ]}
>> pdict.rhymes("beheading", enjambment=True)
{'bɪhˈɛdɪŋ': ['dreading', 'treading', 'read', 'said', ... ]}
```
