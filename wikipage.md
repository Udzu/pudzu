# [wikipage.py](pudzu/experimental/wikipage.py)

## Summary 
Classes for using Wikipedia and Wikidata pages.
 
## Dependencies
*Required*: [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/), [lxml](http://lxml.de/), [requests](http://docs.python-requests.org/en/master/), [pandas](http://pandas.pydata.org/), [toolz](http://toolz.readthedocs.io/en/latest/index.html), [tureen](tureen.md), [dates](dates.md).

*Optional*: [requests_cache](https://requests-cache.readthedocs.io/en/latest/) (for request cacheing)

## Documentation

This module is still fairly preliminary and likely to change. Check source for latest.

### WikiPage

Class representing a Wikipedia page. Initialised from name and language.

```python
>> wp = WikiPage("Groucho") # defaults to lang="en"
>> wp
<WikiPage at Groucho Marx (redirect from Groucho) [en]>
>> wp.title
'Groucho Marx'
>> wp.url
'http://en.wikipedia.org/wiki/Groucho Marx'
>> wp.entity
'Q103846'
>> wp.image_url
'https://upload.wikimedia.org/wikipedia/commons/6/68/Groucho_Marx_-_portrait.jpg'
>> wp.revision_count() # involves API calls
2333
```

Non-basic functionality currently involves accessing the bs4 soup directly:
 
```python
>> bib_h2 = find_tag(wp.bs4, all_(id="Bibliography"), parents_("h2"))
>> next_h2 = find_tag(bib_h2,  next_siblings_("h2", limit=1))
>> find_tags(bib_h2, next_("a", href=re.compile("/wiki/")), exclude_(next_h2, is_after))
[<a href="/wiki/Wikipedia:WikiProject_Lists#Incomplete_lists" title="Wikipedia:WikiProject Lists">incomplete</a>,
 <a href="/wiki/International_Standard_Book_Number" title="International Standard Book Number">ISBN</a>,
 <a href="/wiki/Special:BookSources/0-306-80607-X" title="Special:BookSources/0-306-80607-X">0-306-80607-X</a>,
 <a href="/wiki/International_Standard_Book_Number" title="International Standard Book Number">ISBN</a>,
 <a href="/wiki/Special:BookSources/0-672-52224-1" title="Special:BookSources/0-672-52224-1">0-672-52224-1</a>,
 <a href="/wiki/Otto_Soglow" title="Otto Soglow">Otto Soglow</a>]
```

### WDPage

Class representing a WikiData entity (both items and properties). Can be initialised from an entity code, a name and language, or a Wikipedia page.

```python
>> WDPage(wp.entity)
<WDPage at Q103846 (Groucho Marx)>
>> WDPage.from_name("Γκράουτσο Μαρξ", "el")
<WDPage at Q103846 (Γκράουτσο Μαρξ)>
>> WDPage.from_wikipedia(wp)
<WDPage at Q103846 (Groucho Marx)>
>> wd = _
>> wd.name(lang="he")
גראוצ'ו מרקס
>> wd.countries_of_birth
[<WDPage at Q30 (United States of America)>]
```

Property entries can be initialised by name using the WDProp constructor. Property values can be extracted using `property_values`, which includes some value conversion and qualifier filtering support, though this is still quite rudimentary.

```python
>> WDProp("date of birth")
<WDPage at P569 (date of birth)>
>> wd.property_values('P569')
[2 October 1890 (day) [Gregorian]] # Date type for time values
>> wd.property_values(WDProp("lieu de naissance", "fr"))
[<WDPage at Q60 (New York City)>] # WDPage type for entity values
>> wd.property_values(WDProp("NNDB people ID"))
['855/000031762'] # text type for text values
```

Value conversions can be disabled. More complex calculations currently require looking at the `claims` dict directly.

```python
>> wd.property_values('P569', convert=False)
[{'after': 0,
  'before': 0,
  'calendarmodel': 'http://www.wikidata.org/entity/Q1985727',
  'precision': 11,
  'time': '+1890-10-02T00:00:00Z',
  'timezone': 0}]
>> wd.claims['P570'][0]['mainsnak']['datavalue']
{'type': 'time',
 'value': {'after': 0,
  'before': 0,
  'calendarmodel': 'http://www.wikidata.org/entity/Q1985727',
  'precision': 11,
  'time': '+1977-08-19T00:00:00Z',
  'timezone': 0}}
```

### Cacheing

Both `WikiPage` and `WDPage` support request cacheing using the requests_cache module. To enable this, call the `set_cache` class method on the relevant class.

```python
>> WikiPage.set_cache(r"C:\temp\wikipage", expires_after=86400) # enables cacheing
>> WikiPage.set_cache(None) # disables it
```

