# [tureen.py](tureen.py)

## Summary 
A few utilities for BeautifulSoup.

## Dependencies
*Required*: [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/), [toolz](http://toolz.readthedocs.io/en/latest/index.html), [utils](utils.md).

## Documentation

Like in the BeatifulSoup documentation, the following extract from *Alice in Wonderland* is used as an example throughout:

```python
>> html_doc = """
<html><head><title>The Dormouse's story</title></head>
<body>
<p class="title"><b>The Dormouse's story</b></p>

<p class="story">Once upon a time there were three little sisters; and their names were
<a href="http://example.com/elsie" class="sister" id="link1">Elsie</a>,
<a href="http://example.com/lacie" class="sister" id="link2">Lacie</a> and
<a href="http://example.com/tillie" class="sister" id="link3">Tillie</a>;
and they lived at the bottom of a well.</p>

<p class="story">...</p>
"""
>> soup = BeautifulSoup(html_doc, 'lxml')
```

### Debugging

**print_tags**: print one or more tags, excluding any nested content (alias **pt**).

```python
>> pt(soup.find_all("p"))
<p class="title">
<p class="story">
<p class="story">
```

**print_path**: print the path from the root down to a tag (alias **pp**).

```python
>> pp(soup.find(id="link1"))
<html>
<body>
<p class="story">
<a class="sister" href="http://example.com/elsie" id="link1">
```

### Filtering

**find_tags**: apply a sequence of find methods to a collection of tags. Each method must map a tag to one or more tags. The end result may contain duplicates, which can be removed using remove\_duplicate\_tags. For convenience, the following partial methods are defined: all\_, next\_, prev\_, parents\_, next\_siblings\_, prev\_siblings\_, select\_, exclude\_, restrict\_. These take the same parameters as find_all, find_all_next, find_all_previous, find_parents, find_next_siblings, find_previous_siblings, select, exclude_tags and restrict_tags. 

```python
>> find_tags(soup, "p", all_(href=True), next_siblings_(limit=1))
[<a class="sister" href="http://example.com/lacie" id="link2">Lacie</a>,
 <a class="sister" href="http://example.com/tillie" id="link3">Tillie</a>]
```

**find_tag**: same as find_tags but returns just the first result (or None).

```python
>> find_tag(soup, "a", parents_(limit=1))
<p class="story">Once upon a time there were three little sisters; and their names were
<a class="sister" href="http://example.com/elsie" id="link1">Elsie</a>,
<a class="sister" href="http://example.com/lacie" id="link2">Lacie</a> and
<a class="sister" href="http://example.com/tillie" id="link3">Tillie</a>;
and they lived at the bottom of a well.</p>
```

**re_exclude**: a negated regex filter.

```python
>> find_tags(soup, all_("a", string=re_exclude("E.*e")))
[<a class="sister" href="http://example.com/lacie" id="link2">Lacie</a>,
 <a class="sister" href="http://example.com/tillie" id="link3">Tillie</a>]
```

**is_parent/is_child/is_ancestor/is_descendent/is_before/is_after**: tag comparisons. Useful for exclusions/restrictions, below.

```python
>> is_parent(soup.find(class_="story"), soup.find(id="link1"))
True
>> is_before(soup.find(class_="title"), soup.find(id="link1"))
True
```

**exclude_tags**: filter out tags that are related to at least one of an excluded set.

```python
>> exclude_tags(soup.find_all("a"), soup.find(id="link2"))
[<a class="sister" href="http://example.com/elsie" id="link1">Elsie</a>,
 <a class="sister" href="http://example.com/tillie" id="link3">Tillie</a>]
>> exclude_tags(soup.find_all("p"), soup.find_all("a"), is_parent)
[<p class="title"><b>The Dormouse's story</b></p>, <p class="story">...</p>]
```

**restrict_tags**: restrict to tags that are related to at least one of an included set.

```python
>> restrict_tags(soup.find_all("a"), soup.find(id="link2"))
[<a class="sister" href="http://example.com/lacie" id="link2">Lacie</a>]
>> restrict_tags(soup.find_all("p"), soup.find_all("a"), is_parent)
[<p class="story">Once upon a time there were three little sisters; and their names were
 <a class="sister" href="http://example.com/elsie" id="link1">Elsie</a>,
 <a class="sister" href="http://example.com/lacie" id="link2">Lacie</a> and
 <a class="sister" href="http://example.com/tillie" id="link3">Tillie</a>;
 and they lived at the bottom of a well.</p>]
```

**remove_duplicate_tags**: remove duplicate tags in a list, preserving ordering (useful with find_tags).

```python
>> find_tags(soup, "a", next_siblings_())
[<a class="sister" href="http://example.com/lacie" id="link2">Lacie</a>,
 <a class="sister" href="http://example.com/tillie" id="link3">Tillie</a>,
 <a class="sister" href="http://example.com/tillie" id="link3">Tillie</a>]
>> remove_duplicate_tags(_)
(<a class="sister" href="http://example.com/lacie" id="link2">Lacie</a>,
 <a class="sister" href="http://example.com/tillie" id="link3">Tillie</a>)
```
