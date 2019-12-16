# pudzu

## Summary

Various Python 3.6+ utility modules and scripts, mostly geared towards dataviz and used to create the data visualisations in this [flickr account](https://www.flickr.com/photos/zarfo/albums) (most of which been posted to reddit at some point by [/u/Udzu](https://www.reddit.com/user/Udzu/)). The modules aren't properly tested but are reasonably simple, generic and docstringed.

**Note that the stable modules have now been moved to the [pudzu-packages](https://github.com/Udzu/pudzu-packages) repository.**

## Installation

The stable modules can be installed using `pip` as described in the [pudzu-packages](https://github.com/Udzu/pudzu-packages) repository. Experimental (WIP) models can be installed using `pip install pudzu` (for the latest release) or by directly running `python setup.py install`.

## Stable modules
- [pudzu-utils](https://github.com/Udzu/pudzu-packages/tree/master/pudzu-utils) - various utility functions and data structures.
- [pudzu-dates](https://github.com/Udzu/pudzu-packages/tree/master/pudzu-dates) - date classes supporting flexible calendars, deltas and ranges.
- [pudzu-pillar](https://github.com/Udzu/pudzu-packages/tree/master/pudzu-pillar) - various monkey-patched Pillow utilities.
- [pudzu-charts](https://github.com/Udzu/pudzu-packages/tree/master/pudzu-charts) - Pillow-based charting tools.

## Experimental modules

- [pudzu.experimental.markov](markov.md) - simple Markov Chain n-gram based generator.
- [pudzu.experimental.nounce](nounce.md) - simple IPA-based pronouncing and rhyming dictionary.
- [pudzu.experimental.tureen](tureen.md) - various BeautifulSoup utilities.
- [pudzu.experimental.wikipage](wikipage.md) - wikipedia and wikidata parsing utilities.

## Copyright

Copyright © 2017–19 by Udzu. Licensed under the [MIT License](LICENSE).
