# pudzu

## Summary

Various Python 3.6+ utility functions, mostly geared towards dataviz and used to create the data visualisations in this [flickr account](https://www.flickr.com/photos/zarfo/albums). Most have been posted to reddit at some point by [/u/Udzu](https://www.reddit.com/user/Udzu/).

The modules aren't properly tested or packaged up (yet) but are reasonably simple, generic and docstringed. They are not optimised for speed or resilience. They are targeted at for-fun, interactive work.

## Modules

### General modules
- [utils.py](utils.md) - various utility functions and data structures.
- [dates.py](dates.md) - date classes supporting flexible calendars, deltas and ranges.
- [markov.py](markov.md) - simple Markov Chain n-gram based generator.
- [nounce.py](nounce.md) - simple IPA-based pronouncing and rhyming dictionary.

### Dataviz modules
- [bamboo.py](bamboo.md) - various monkey-patched pandas utilities.
- [pillar.py](pillar.md) - various monkey-patched Pillow utilities.
- [charts.py](charts.md) - Pillow-based charting tools.
- [tureen.py](tureen.md) - various BeautifulSoup utilities.
- [wikipage.py](wikipage.md) - wikipedia and wikidata parsing utilities.

## Copyright

Copyright © 2017–18 by Udzu. Licensed under the [MIT License](LICENSE).
