# charts.py

## Summary 
Pillow-based charting.
 
## Dependencies
*Required*: [pillow](http://pillow.readthedocs.io/en/4.2.x/index.html), [toolz](http://toolz.readthedocs.io/en/latest/index.html), [pillar](pillar.md), [utils](utils.md).

*Optional*: [pandas](http://pandas.pydata.org/) (for dataframe-based charts), [dates](dates.md) (for flexible time charts).

## Documentation

Three chart types are currently supported: **bar charts**, **time charts** and **grid charts**. For usage information, see the docstrings and sample scripts.

### Bar charts

**bar_chart**: generate a bar chart; supports grouped, stacked and percentage stacked charts.

![bar chart example](images/example1_small.png)

### Time charts

**time_chart**: generate a time chart; supports numeric and date timelines.

![time chart example](images/example2_small.png)

### Grid charts

**grid_chart**: generate an image grid chart; essentially a convenient wrapper for `Image.from_array`.

![grid chart example](images/example3_small.png)

![grid chart example](images/example4_small.png)
