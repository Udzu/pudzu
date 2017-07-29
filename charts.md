# [charts.py](charts.py)

## Summary 
Pillow-based charting.
 
## Dependencies
*Required*: [pillow](http://pillow.readthedocs.io/en/4.2.x/index.html), [toolz](http://toolz.readthedocs.io/en/latest/index.html), [pillar](pillar.md), [utils](utils.md).

*Optional*: [pandas](http://pandas.pydata.org/) (for dataframe-based charts), [dates](dates.md) (for flexible time charts).

## Documentation

Three chart types are currently supported: **bar charts**, **time charts** and **grid charts**. For usage information, see the docstrings and [sample scripts](dataviz/).

### Bar charts

**bar_chart**: generate a bar chart; supports grouped, stacked and percentage stacked charts. Sample script: [ukelections.py](dataviz/ukelections.py).

![uk elections bar chart](images/chart_elections.png)

### Time charts

**time_chart**: generate a time chart; supports numeric and date timelines. Sample script: [g7.py](dataviz/g7.py).

![time chart example](images/chart_g7.png)

### Grid charts

**grid_chart**: generate an image grid chart; essentially a convenient wrapper for `Image.from_array`. Sample scripts: [periodic.py](dataviz/periodic.py) and [40under40.py](dataviz/40under40.py).

![grid chart example](images/chart_periodic.png)

![grid chart example](images/chart_40under40.png)

### Map charts

**map_chart**: generate a map chart; essentially a convenient wrapper for Image.replace/select_color. Input is a map tempalte with each region having a unique color. Regions can be named (see generate_name_csv) and label bounding boxes can be defined (see generate_labelbox_csv).