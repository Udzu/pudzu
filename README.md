# pudzu

## Summary

Various Python 3.6+ utility functions, mostly geared towards dataviz and used to create the data visualisations in this [flickr account](https://www.flickr.com/photos/zarfo/albums) (most of which been posted to reddit at some point by [/u/Udzu](https://www.reddit.com/user/Udzu/)). The modules aren't properly tested but are reasonably simple, generic and docstringed.

## Installation

The packaged modules can be installed using `pip install pudzu` (for the latest release) or by directly running `python setup.py install`.

## Packaged modules

- [pudzu.utils](utils.md) - various utility functions and data structures.
- [pudzu.dates](dates.md) - date classes supporting flexible calendars, deltas and ranges.
- [pudzu.bamboo](bamboo.md) - various monkey-patched pandas utilities.
- [pudzu.pillar](pillar.md) - various monkey-patched Pillow utilities.
- [pudzu.charts](charts.md) - Pillow-based charting tools.
- [pudzu.tureen](tureen.md) - various BeautifulSoup utilities.

## Unpackaged modules

- [markov.py](markov.md) - simple Markov Chain n-gram based generator.
- [nounce.py](nounce.md) - simple IPA-based pronouncing and rhyming dictionary.
- [wikipage.py](wikipage.md) - wikipedia and wikidata parsing utilities.

## Copyright

Copyright © 2017–19 by Udzu. Licensed under the [MIT License](LICENSE).
