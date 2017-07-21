# pudzu

## Summary

Various Python utility functions, mostly geared towards dataviz and used to create visualisations such as this [bar chart](https://raw.githubusercontent.com/Udzu/pudzu/master/images/chart_elections.png), [time chart](https://raw.githubusercontent.com/Udzu/pudzu/master/images/chart_g7.png), [periodic table](https://raw.githubusercontent.com/Udzu/pudzu/master/images/chart_periodic.png)  and [image grid](https://raw.githubusercontent.com/Udzu/pudzu/master/images/chart_40under40.png).

The modules aren't properly packaged up or pip-able but are reasonably simple, generic and docstringed. They are not optimised for speed or tested for resilience. They are targeted at for-fun, interactive work.

## Modules

- [utils.py](utils.md) - various utility functions and data structures.
- [dates.py](dates.md) - date classes supporting flexible calendars, deltas and ranges.
- [records.py](records.md) - utilities for functional handling of records (lists of dicts).
- *pillar.py* - various monkey-patched Pillow utilities.
- *charts.py* - Pillow-based charting tools.
- *tureen.py* - various BeautifulSoup utilities.
- *wikipage.py* - wikipedia and wikidata parsing utilities.

## Copyright

Copyright © 2017 by Udzu. Licensed under the [MIT License](LICENSE).
