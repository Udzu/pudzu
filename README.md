# pudzu

## Summary

Various Python 3.8+ utility modules and scripts, mostly geared towards dataviz and used to create the data visualisations in this [flickr account](https://www.flickr.com/photos/zarfo/albums) (most of which been posted to reddit at some point by [/u/Udzu](https://www.reddit.com/user/Udzu/)). The modules aren't properly tested but are reasonably simple, generic and docstringed.

**Note that the stable modules have now been moved to the [pudzu-packages](https://github.com/Udzu/pudzu-packages) repository.**

## Installation

The stable modules can be installed using `pip` as described in the [pudzu-packages](https://github.com/Udzu/pudzu-packages) repository. Experimental (WIP) models can be installed using `pip install pudzu` (for the latest release) or by directly running `pip install .`.

## Stable modules
- [pudzu-utils](https://github.com/Udzu/pudzu-packages/tree/master/pudzu-utils) - various utility functions and data structures.
- [pudzu-dates](https://github.com/Udzu/pudzu-packages/tree/master/pudzu-dates) - date classes supporting flexible calendars, deltas and ranges.
- [pudzu-patterns](https://github.com/Udzu/pudzu-packages/tree/master/pudzu-patterns) - NFA-based pattern matcher supporting novel operations and modifiers.
- [pudzu-pillar](https://github.com/Udzu/pudzu-packages/tree/master/pudzu-pillar) - various monkey-patched Pillow utilities.
- [pudzu-charts](https://github.com/Udzu/pudzu-packages/tree/master/pudzu-charts) - Pillow-based charting tools.

## WIP modules

- [pudzu.sandbox.bamboo](bamboo.md) - various monkey-patched Pandas utilities.
- [pudzu.sandbox.markov](markov.md) - simple Markov Chain n-gram based generator.
- [pudzu.sandbox.nounce](nounce.md) - simple IPA-based pronouncing and rhyming dictionary.
- pudzu.sandbox.tinytim - simple turtle-based LSystem renderer.
- [pudzu.sandbox.tureen](tureen.md) - various BeautifulSoup utilities.
- [pudzu.sandbox.unicode](unicode.md) - Unicode-related data and utilities.
- [pudzu.sandbox.wikipage](wikipage.md) - wikipedia and wikidata parsing utilities.

## Copyright

Copyright © 2017–20 by Udzu. Licensed under the [MIT License](LICENSE).
