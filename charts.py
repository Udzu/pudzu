from bamboo import *
from pillar import *
from os.path import splitext
from enum import Enum

# Random collection of Pillow-based charting functions

logger = logging.getLogger('charts')

# Legends

def generate_legend(boxes, labels, box_sizes=40, fonts=papply(arial, 16), fg="black", bg="white",
                    header=None, footer=None, max_width=None, spacing=0, box_mask=None, border=True):
    """Generate a chart category legend.
    - boxes (list of colors/images): colors or images to use as boxes
    - labels (list of strings/images/lists): labels to use beside the boxes
    - box_sizes (int/(int,int)/list of (int,int)): size(s) of boxes to use for colors; height can be set to ... [40x40]
    - fonts (font/three fonts/font function): normal, bold and italics fonts [16-point arial]
    - fg (color): text and border color [black]
    - bg (color): background color [white]
    - header (string/image/None): header at top of legend, bolded if text [None]
    - footer (string/image/None): footer at bottom of legend, italicised if text [None]
    - max_width (int/None): legend width limit, excluding border and padding [None]
    - spacing (int): vertical spacing between categories [0]
    - box_mask(image): optional mask to apply over the boxes [None]
    - border (boolean): whether to include a border [True]
    """
    if len(labels) != len(boxes):
        raise ValueError("Different number of labels ({}) to boxes ({})".format(len(labels), len(boxes)))
    if isinstance(box_sizes, Integral):
        box_sizes = (box_sizes, box_sizes)
    if non_string_sequence(box_sizes, (Integral, type(...))):
        box_sizes = [box_sizes]*len(labels)
    if len(boxes) != len(box_sizes):
        raise ValueError("Different number of boxes ({}) to box sizes ({})".format(len(boxes), len(box_sizes)))
    if any(not isinstance(box, Image.Image) and non_string_sequence(label) and size[1] == ... for box, label, size in zip(boxes, labels, box_sizes)):
        raise ValueError("Cannot specify both list of labels and ... height for the same box")
    if callable(fonts):
        fonts = [fonts(), fonts(bold=True), fonts(italics=True)]
    elif isinstance(fonts, ImageFont.FreeTypeFont):
        fonts = [fonts]*3
    if isinstance(header, str):
        header = Image.from_text(header, fonts[1], fg=fg, bg=bg, max_width=max_width, padding=2)
    if isinstance(footer, str):
        footer = Image.from_text(footer, fonts[2], fg=fg, bg=bg, max_width=max_width, padding=2)
        
    max_box_width = max(box.width if isinstance(box, Image.Image) else size[0] for box, size in zip(boxes, box_sizes))
    max_label_width = None if max_width is None else max_width - max_box_width - 8
    
    box_label_array = []
    for box, label, size in zip(boxes, labels, box_sizes):
        if isinstance(label, str):
            label = Image.from_text(label, fonts[0], fg=fg, bg=bg, max_width=max_label_width, padding=2)
        if not isinstance(box, Image.Image):
            box = Image.new("RGBA", (size[0], size[1] if size[1] != ... else label.height + 6), box)
        if non_string_sequence(label):
            labels = label
            label = Image.new("RGBA", box.size, bg)
            offsets = Padding(0)
            for i, l in enumerate(labels):
                if isinstance(l, str):
                    l = Image.from_text(l, fonts[0], fg=fg, bg=bg, max_width=max_label_width, padding=2)
                label = label.pin(l, (0, (box.height * i) // (len(labels) - 1)), align=(0, 0.5), bg=bg, offsets=offsets)
        box_label_array.append([box, label])
    label_img = Image.from_array(box_label_array, padding=(1,spacing), xalign=[0.5, 0], bg=bg)
    
    if box_mask is not None:
        boxes_size = (max_box_width, label_img.height - 2*spacing*len(box_label_array))
        label_img = label_img.overlay(Image.new("RGBA", boxes_size, bg), (1,spacing), mask=box_mask.resize(boxes_size).invert_mask())
    
    legend = Image.from_column([i for i in [header, label_img, footer] if i is not None], padding=(2,3), xalign=0, bg=bg)
    
    if border: legend = legend.pad(2,bg).pad(1, fg)
    return legend
    
# Bar charts

VEGA_PALETTE = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]

class BarChartType(Enum):
    """Bar Chart types."""
    SIMPLE, STACKED, STACKED_PERCENTAGE = range(3)

class BarChartLabelPosition(Enum):
    """Bar Chart label position."""
    AXIS, OUTSIDE, INSIDE, ABOVE, BELOW = range(5)

def bar_chart(data, bar_width, chart_height, type=BarChartType.SIMPLE,
              fg="black", bg="white", spacing=0, group_spacing=0,
              ymin=None, ymax=None, grid_interval=None,
              tick_interval=Ellipsis, label_interval=Ellipsis, ylabels=None, yformat=None, 
              colors=VEGA_PALETTE, clabels=None, rlabels=None,
              xlabel=None, ylabel=None, title=None,
              legend_position=None, legend_fonts=papply(arial, 16),legend_box_sizes=(40,40), legend_args={}):
    """Plot a bar chart.
    - data (pandas dataframe): table to plot
    - bar_width (int): bar width
    - chart_height (int): chart height
    - type (BarChartType): type of bar chart [BarChartType.SIMPLE]
    - fg (color): axes and font color [black]
    - bg (color): background color [white]
    - spacing (int): column spacing either side of groups [0]
    - group_spacing (int): column spacing either side of bars within a group [0]
    - ymin (float): minimum y value [auto]
    - ymax (float): maximum y value [auto]
    - grid_interval (float): grid line interval [zero line only]
    - tick_interval (float): tick line interval [grid_interval]
    - label_interval (float): y label interval [grid_interval]
    - ylabels (value -> image/font): image or font to use for y-axis labels [none]
    - yformat (string/value->string): formatting for y values if ylabels is a font [3 sig figs, or % for stacked]
    - colors (col, row, value -> color/image/(size->image)): color or image to use for bars [Vega palette]
    - clabels (col, row, value -> image/font): image or font to use for column labels; optionally a dict keyed by BarChartLabelPosition [none]
    - rlabels (row -> image/font): image or font to use for row labels; optionally a dict keyed by BarChartLabelPosition [none]
    - xlabel (image): image to use for x axis label [none]
    - ylabel (image): image to use for y axis label [none]
    - title (image): image to use for title [none]
    - legend_position (alignment): legend alignment [None]
    - legend_fonts (font/three fonts/font function): normal, bold and italics fonts [16-point arial]
    - legend_box_sizes (col->int/(int,int)): sizes to use for legend boxes [40x40]
    - legend_args (dict): additional arguments to generate legends [none]
    Functional arguments don't need to accept all the arguments and can also be passed in as
    constants or lists instead.
    """
    
    # Arguments and defaults
    if type == BarChartType.SIMPLE:
        if ymin is None:
            ymin = min(0, floor_significant(data.values.min(), 1))
        if ymax is None:
            ymax = max(0, ceil_significant(data.values.max(), 1))
        if ymin >= ymax:
            raise ValueError("Mininum y value {0:.3g} must be smaller than maximum y vaue {0:.3g}".format(ymin, ymax))
    elif type == BarChartType.STACKED:
        if data.values.min() < 0:
            raise ValueError("Stacked charts don't support negative values.")
        if ymin not in [None, 0]:
            raise ValueError("Cannot set minimum y value for stacked charts.")
        ymin = 0
        maxsum = max(sum(row) for row in data.values)
        if ymax is None:
            ymax = max(0, ceil_significant(maxsum, 1))
        elif ymax < maxsum:
            raise ValueError("Maximum y value {0:.3g} must be no smaller than maximum stack size {0:.3g}".format(ymax, maxsum))
    elif type == BarChartType.STACKED_PERCENTAGE:
        if data.values.min() < 0:
            raise ValueError("Stacked percentage charts don't support negative values.")
        if ymin not in [None, 0] or ymax not in [None, 1]:
            raise ValueError("Cannot set minimum/maximum y values for stacked percentage charts.")
        ymin = 0
        ymax = 1
      
    clabel_dict = make_mapping(clabels, lambda: BarChartLabelPosition.AXIS if type == BarChartType.SIMPLE else BarChartLabelPosition.INSIDE)
    rlabel_dict = make_mapping(rlabels, lambda: BarChartLabelPosition.BELOW)
    
    if type == BarChartType.SIMPLE:
        if not all(k in [BarChartLabelPosition.ABOVE, BarChartLabelPosition.BELOW] for k in rlabel_dict.keys()):
            raise ValueError("Row labels in simple charts must above or below the chart.")
    else:
        if any(k != BarChartLabelPosition.INSIDE for k in clabel_dict.keys()):
            raise ValueError("Column labels in stacked charts must be inside the bar.")
        if not all(k in [BarChartLabelPosition.ABOVE, BarChartLabelPosition.BELOW, BarChartLabelPosition.OUTSIDE] for k in rlabel_dict.keys()):
            raise ValueError("Row labels in stacked charts must above, below or outside the bar.")
            
    if grid_interval is None:
        grid_interval = max(abs(ymin), ymax) * 2
    if tick_interval is Ellipsis:
        tick_interval = grid_interval
    if label_interval is Ellipsis:
        label_interval = grid_interval

    def make_fn_arg(input):
        if non_string_iterable(input) and not all(isinstance(x, Integral) for x in input): return lambda *args: input[args[0] % len(input)]
        elif not callable(input): return lambda *args: input
        else: return ignoring_extra_args(input)

    color_fn = make_fn_arg(colors)
    clabel_dict = valmap(make_fn_arg, clabel_dict)
    rlabel_dict = valmap(make_fn_arg, rlabel_dict)
    ylabel_fn = make_fn_arg(ylabels)
    lsize_fn = make_fn_arg(legend_box_sizes)
    if legend_position: lalign = Alignment(legend_position)

    if yformat is None:
        yformat = "{:.0%}" if type == BarChartType.STACKED_PERCENTAGE else "{0:.3g}"
    yformat_fn = yformat if callable(yformat) else lambda v: yformat.format(v)

    # Helpers
    tick_size = 0 if tick_interval is None else bar_width // 4
    factor = chart_height / (ymax - ymin)
    positive_height_fn = lambda v: int(max(0, min(v, ymax) - max(0, ymin)) * factor)
    negative_height_fn = lambda v: int(max(0, min(0, ymax) - max(v, ymin)) * factor)
    y_coordinate_fn = lambda v: int(chart_height - ((v - ymin) * factor))
    bgtransparent = ImageColor.getrgba(bg)._replace(alpha=0)
    
    def make_box(fill, size):
        if callable(fill): return fill(size)
        elif isinstance(fill, Image.Image): return fill.resize(size)
        else: return Image.new("RGBA", size, fill)
    
    # Bars
    groups = []
    for r, row in enumerate(data.values):
        group_bars = []
        for c, v in enumerate(row):
            if type == BarChartType.STACKED_PERCENTAGE:
                v = v / sum(row)
            fill = color_fn(c,r,v)
            pbar = make_box(fill, (bar_width, positive_height_fn(v)))
            nbar = make_box(fill, (bar_width, negative_height_fn(v)))
            
            def with_inside_label(bar):
                if BarChartLabelPosition.INSIDE in clabel_dict:
                    label = clabel_dict[BarChartLabelPosition.INSIDE](c,r,v,bar.width,bar.height)
                    if label is not None:
                        if isinstance(label, ImageFont.FreeTypeFont):
                            label = Image.from_text(str(data.columns[c]), label, fg=fg, bg=bgtransparent)
                        return bar.place(label)
                return bar
                    
            if type in [BarChartType.STACKED, BarChartType.STACKED_PERCENTAGE]:
                bar = with_inside_label(pbar)
            else:
                if nbar.height > 0: nbar = with_inside_label(nbar)
                else: pbar = with_inside_label(pbar)
                pbar = pbar.pad_to_aspect(pbar.width, positive_height_fn(ymax), align=1, bg=0)
                nbar = nbar.pad_to_aspect(nbar.width, negative_height_fn(ymin), align=0, bg=0)
                bar = Image.from_column([pbar, Image.new("RGBA",(0,1)), nbar])
            group_bars.append(bar)
        if type in [BarChartType.STACKED, BarChartType.STACKED_PERCENTAGE]:
            group = Image.from_column(reversed(group_bars), bg=bgtransparent)
            group = group.pad_to_aspect(group.width, chart_height, align=1, bg=0)
            group = group.pad((0,0,0,1), bg=0)
        else:
            group = Image.from_row(group_bars, padding=(group_spacing,0), bg=bgtransparent, yalign=0)
        groups.append(group)
    chart = Image.from_row(groups, padding=(spacing,0), bg=bgtransparent, yalign=0)
    
    # Legend
    if legend_position is not None:
        boxes, labels, box_sizes = [], [], []
        for c in range(len(data.columns)):
            fill = color_fn(c,0,0)
            boxes.append(make_box(fill, lsize_fn(c)) if callable(fill) or isinstance(fill, Image.Image) else fill)
            box_sizes.append(lsize_fn(c))
            labels.append(str(data.columns[c]))
        legend = generate_legend(boxes=boxes, labels=labels, box_sizes=box_sizes, fonts=legend_fonts,  fg=fg, bg=bg, **legend_args)
        chart = chart.place(legend.pad(10,0), lalign)

    # Keep track of offsets relative to chart
    offsets = Padding(0)
    
    # Grid
    chart = chart.pad((tick_size,0,0,0), bg=0, offsets=offsets)
    grid = Image.new("RGBA", (chart.width, chart.height), (255,255,255,0))
    gridcolor = ImageColor.getrgba(fg)._replace(alpha=80)
    griddraw = ImageDraw.Draw(grid)
    griddraw.line([(tick_size, y_coordinate_fn(ymin)), (tick_size, y_coordinate_fn(ymax))], fill=fg)
    if grid_interval is not None:
        for i in range(ceil(ymin / grid_interval), floor(ymax / grid_interval) + 1):
            y = y_coordinate_fn(i * grid_interval)
            griddraw.line([(tick_size, y), (chart.width, y)], fill=fg if i == 0 else gridcolor)
    if tick_interval is not None:
        for i in range(ceil(ymin / tick_interval), floor(ymax / tick_interval) + 1):
            y = y_coordinate_fn(i * tick_interval)
            griddraw.line([(0, y), (tick_size, y)], fill=fg)
    del griddraw
    chart = Image.alpha_composite(grid, chart)
    
    # Numeric labels
    if label_interval is not None and ylabels is not None:
        for i in range(ceil(ymin / label_interval), floor(ymax / label_interval) + 1):
            y = i * label_interval
            label = ylabel_fn(y)
            if isinstance(label, ImageFont.FreeTypeFont):
                label = Image.from_text(yformat_fn(y), label, fg=fg, bg=bg)
            chart = chart.pin(label, (-tick_size-10, y_coordinate_fn(y)), align=(1,0.5), bg=bg, offsets=offsets)
       
    # Column labels
    for clabels_pos, clabel_fn in clabel_dict.items():
        if clabels_pos == BarChartLabelPosition.INSIDE: continue
        for r, row in enumerate(data.values):
            for c, v in enumerate(row):
                label = clabel_fn(c,r,v)
                if label is None:
                    continue
                elif isinstance(label, ImageFont.FreeTypeFont):
                    label = Image.from_text(str(data.columns[c]), label, fg=fg, bg=bg, padding=(0,2))
                x = (r * (len(data.columns) * (bar_width + 2 * group_spacing) + 2 * spacing) +
                     spacing + c * (bar_width + 2 * group_spacing) + group_spacing + bar_width // 2)
                if clabels_pos == BarChartLabelPosition.AXIS:
                    y = y_coordinate_fn(0) + int(v >= 0)
                elif clabels_pos == BarChartLabelPosition.OUTSIDE:
                    y = y_coordinate_fn(v) + int(v < 0)
                elif clabels_pos == BarChartLabelPosition.ABOVE:
                    y = y_coordinate_fn(ymax) + int(v <= 0)
                elif clabels_pos == BarChartLabelPosition.BELOW:
                    y = y_coordinate_fn(ymin) + int(v <= 0)
                label_at_top = y <= y_coordinate_fn(0)
                chart = chart.pin(label, (x, y), align=(0.5,int(label_at_top)), bg=bg, offsets=offsets)
    
    # Row labels
    for rlabels_pos, rlabel_fn in rlabel_dict.items():
        for r, row in enumerate(data.values):
            label = rlabel_fn(r)
            if label is None:
                continue
            elif isinstance(label, ImageFont.FreeTypeFont):
                label = Image.from_text(str(data.index[r]), label, fg=fg, bg=bg, padding=(0,2))
            if type in [BarChartType.STACKED, BarChartType.STACKED_PERCENTAGE]:
                x = (r * (bar_width + 2 * spacing) + (bar_width + 2 * spacing) // 2)
            else:
                x = (r * (len(data.columns) * (bar_width + 2 * group_spacing) + 2 * spacing) +
                     (len(data.columns) * (bar_width + 2 * group_spacing) + 2 * spacing) // 2)
            if rlabels_pos ==  BarChartLabelPosition.ABOVE:
                chart = chart.pin(label, (x, 0), align=(0.5,1), bg=bg, offsets=offsets)
            elif rlabels_pos ==  BarChartLabelPosition.BELOW:
                chart = chart.pin(label, (x, chart.height - offsets.y), align=(0.5,0), bg=bg, offsets=offsets)
            # TODO: support OUTSIDE rlabels in stacked mode
        
    # Background
    background = Image.new("RGBA", (chart.width, chart.height), bg)
    chart = Image.alpha_composite(background, chart)
    
    # Labels and title
    if xlabel is not None or ylabel is not None:
        chart = Image.from_array([[ylabel or Image.EMPTY_IMAGE, chart], [Image.EMPTY_IMAGE, xlabel or Image.EMPTY_IMAGE]], bg=bg)
    if title is not None:
        chart = Image.from_column((title, chart), bg=bg)
    
    return chart

# Time charts

class TimeChartLabelPosition(Enum):
    """Time Chart label position."""
    INSIDE, ABOVE, BELOW = range(3)

def time_chart(data, chart_width, timeline_height, start_key, end_key, color_key, 
               labels=None, xmin=None, xmax=None, fg="white", bg="black",
               grid_interval=None, grid_font=None, grid_labels=str, grid_label_interval=Ellipsis, 
               label_font=None, labels_left=None, labels_right=None, title=None):
    """Plot a time chart. Times can be numeric, dates or anything that supports arithmetic.
    - data (pandas dataframes): one or more dataframes containing time series
    - chart_width (int): chart width
    - timeline_height (int): height for each timeline
    - start_key (key or series->time): start time for a given entry
    - end_key (key or series->time): end time for a given entry
    - color_key (key or series,width,height->color/image): background for a given entry
    - labels (series,width,height->image/string): label for a given entry; optionally a dict keyed by TimeChartLabelPosition(s) [none]
    - xmin (time): chart start time [auto]
    - xmax (time): chart end time [auto]
    - fg (color): text and grid color [white]
    - bg (color): background color [black]
    - grid_interval (timedelta): grid line interval from start [start and end only]
    - grid_font (font): font to use for grid time labels [none]
    - grid_labels (time->image/string): grid time labels [str]
    - grid_label_interval (timedelta): grid time label interval [grid_interval]
    - label_font (font): font to use for text timeline labels [none]
    - labels_left (images/strings): timeline labels on the left [none]
    - labels_right (images/strings): timeline info on the right [none]
    - title (image): image to use for title [none]
    Functional arguments don't need to accept all the arguments and can also be passed in as
    constants.
    """

    data, labels_left, labels_right = make_sequence(data), make_sequence(labels_left), make_sequence(labels_right),
    start_fn = start_key if callable(start_key) else lambda d: get_non(d, start_key)
    end_fn = end_key if callable(end_key) else lambda d: get_non(d, end_key)
    color_fn = color_key if callable(color_key) else lambda d: get_non(d, color_key)
    grid_label_fn = grid_labels if callable(grid_labels) else lambda v: grid_labels
    labels_dict = make_mapping(labels, lambda: TimeChartLabelPosition.INSIDE)
    labels_dict = { frozenset(make_iterable(k)): v for k,v in labels_dict.items() }
    
    if xmin is None:
        xmin = min(start_fn(d) for df in data for _,d in df.iterrows())
    if xmax is None:
        xmax = max(end_fn(d) for df in data for _,d in df.iterrows())
    if xmin >= xmax:
        raise ValueError("Mininum x value {0:.3g} must be smaller than maximum x vaue {0:.3g}".format(xmin, xmax))
    def xvalue(x):
        return int((delimit(x,xmin,xmax) - xmin) / (xmax - xmin) * chart_width )
    if grid_interval is None:
        grid_interval = xmax-xmin
    if grid_label_interval is Ellipsis:
        grid_label_interval = grid_interval
    
    # chart
    logger.info("Generating time chart")
    timelines, llabels, rlabels, toffsets = [], [], [], []
    for df, llabel, rlabel in zip_longest(data, labels_left, labels_right):
        timeline = Image.new("RGBA", (chart_width, timeline_height), bg)
        nextpos = { pos: None for pos in labels_dict }
        offsets = Padding(0)
        for _,d in df.iterrows():
            start, end = xvalue(start_fn(d)), xvalue(end_fn(d))
            w, h = end-start, timeline_height
            if w == 0: continue
            color = ignoring_extra_args(color_fn)(d, w, h)
            bar = color.resize((w, h)) if isinstance(color, Image.Image) else Image.new("RGBA", (w, h), color)
            bar = bar.trim((1,0, 0, 0)).pad((1,0), bg)
            timeline.overlay(bar, (start+offsets.l, offsets.u))
            for pos, label in labels_dict.items():
                img = ignoring_extra_args(label if callable(label) else lambda d: label)(d, bar.width, bar.height)
                if isinstance(img, str):
                    img = Image.from_text(img, label_font, fg=fg, padding=2)
                if TimeChartLabelPosition.INSIDE in pos and img.width < bar.width and img.height < bar.height:
                    timeline = timeline.pin(img, ((start+end)//2, timeline_height//2), bg=bg, offsets=offsets)
                elif TimeChartLabelPosition.ABOVE in pos and nextpos[pos] != TimeChartLabelPosition.BELOW:
                    timeline = timeline.pin(img, ((start+end)//2, 0), align=(0.5,1), bg=bg, offsets=offsets)
                    if TimeChartLabelPosition.BELOW in pos: nextpos[pos] = TimeChartLabelPosition.BELOW
                elif TimeChartLabelPosition.BELOW in pos:
                    timeline = timeline.pin(img, ((start+end)//2, timeline_height), align=(0.5,0), bg=bg, offsets=offsets)
                    if TimeChartLabelPosition.ABOVE in pos: nextpos[pos] = TimeChartLabelPosition.ABOVE
        timelines.append(timeline)
        toffsets.append(offsets)
        
        if any(labels_left):
            if isinstance(llabel, str):
                llabel = Image.from_text(llabel, label_font, fg=fg, bg=bg, padding=2)
            llabels.append(llabel)
        if any(labels_right):
            if not isinstance(rlabel, Image.Image):
                rlabel = Image.from_text(rlabel, label_font, fg=fg, bg=bg, padding=2)
            rlabels.append(rlabel)
        
    maxoffset = max(o.l for o in toffsets)
    timelines = [ t.pad((maxoffset - o.l,0,0,0), bg=bg) for t,o in zip(timelines, toffsets) ]
    array = list(zip(*[x for x in (llabels, timelines, rlabels) if x]))
    xalign = [a for a,x in zip((1, 0, 0), (llabels, timelines, rlabels)) if x]
    chart = Image.from_array(array, padding=(4,5), bg=bg, xalign=xalign)
    
    # grid
    logger.info("Generating time chart grid and labels")
    xoffset = maxoffset + 4 + (max(label.width for label in llabels)+4*2 if llabels else 0)
    grid = Image.new("RGBA", (chart.width, chart.height), (255,255,255,0))
    gridcolor = ImageColor.getrgba(fg)._replace(alpha=127)
    griddraw = ImageDraw.Draw(grid)
    if grid_interval is not None:
        grid_val = xmin
        while grid_val <= xmax:
            griddraw.line([(xoffset+xvalue(grid_val),0),(xoffset+xvalue(grid_val),chart.height)], fill=gridcolor)
            grid_val += grid_interval
    del griddraw
    chart = Image.alpha_composite(chart, grid)
    
    # grid labels
    if grid_label_interval is not None and grid_font is not None:
        offsets = Padding(0)
        yoffset = chart.height
        grid_val = xmin
        while grid_val <= xmax:
            label = grid_label_fn(grid_val)
            if isinstance(label, str):
                label = Image.from_text(label, grid_font, fg=fg, bg=bg, padding=(0,5,0,0))
            chart = chart.pin(label, (xoffset+xvalue(grid_val), yoffset), align=(0.5,0), bg=bg, offsets=offsets)
            grid_val += grid_label_interval
    
    if title is not None: chart = Image.from_column((title, chart), bg=bg)
    return chart

# Image grids

def grid_chart(data, image_key, image_process=None,
               fg="white", bg="black", xalign=0.5, yalign=0.5, padding=(0,0,0,0),
               row_label=None, col_label=None, title=None):
    """Plot an image grid chart. A fairly simple wrapper for Image.from_array.
    - data (pandas dataframe): table to base chart on
    - image_key (datavalue,row,column->image/url/None): image, cached url or None for each grid cell
    - image_process (image,datavalue,row,column->image): post-processing for all images [none]
    - fg (color): font color [white]
    - bg (color): background color [black]
    - xalign (0 to 1): cell x alignment [center]
    - yalign (0 to 1): cell y alignment [center]
    - padding (Padding): cell padding [0]
    - row_label (row, rowvalues -> image/font): image or font for row labels [none]
    - col_label (col, colvalues -> image/font): image or font for column labels [none]
    - title (image): image to use for title [none]
    Functional arguments don't need to accept all the arguments and can also be passed in as
    constants.
    """
    
    image_fn = ignoring_extra_args(image_key) if callable(image_key) else lambda v: image_key
    process_fn = ignoring_extra_args(image_process) if callable(image_process) else lambda i, v: image_process
    row_label_fn = ignoring_extra_args(row_label) if callable(row_label) else lambda r, vs: row_label
    col_label_fn = ignoring_extra_args(col_label) if callable(col_label) else lambda c, vs: col_label
    
    img_array = [[None for _ in data.columns] for _ in data.index]
    for r, row in enumerate(data.values):
        for c, v in enumerate(row):
            img = image_fn(v, r, c)
            if img is None:
                continue
            elif isinstance(img, str):
                img = Image.from_url_with_cache(img) if urlparse(img).netloc != "" else Image.open(img)
            if image_process is not None:
                img = process_fn(img, v, r, c)
            img_array[r][c] = img

    if row_label is not None:
        for r, row in enumerate(data.values):
            label = row_label_fn(r, list(row))
            if isinstance(label, ImageFont.FreeTypeFont):
                label = Image.from_text(str(data.index[r]), label, fg=fg, bg=bg, padding=(10,2))
            img_array[r].insert(0, label)
            
    if col_label is not None:
        col_labels = [] if row_label is None else [None]
        for c, col in enumerate(data.values.transpose()):
            label = col_label_fn(c, list(col))
            if isinstance(label, ImageFont.FreeTypeFont):
                label = Image.from_text(str(data.columns[c]), label, fg=fg, bg=bg, padding=(2,10))
            col_labels.append(label)
        img_array.insert(0, col_labels)
            
    chart = Image.from_array(img_array, padding=padding, xalign=xalign, yalign=yalign, bg=bg)
    
    if title is not None: chart = Image.from_column((title, chart), bg=bg)
    return chart

# Map charts

class ImageMapSort(Enum):
    """Image map color sort in name CSV file."""
    USAGE, HORIZONTAL, VERTICAL = range(3)
    
def labelbox_img_path(map): return splitext(map)[0] + "_lbox" + splitext(map)[1]
def overlay_img_path(map): return splitext(map)[0] + "_ov" + splitext(map)[1]
def overlay_mask_img_path(map): return splitext(map)[0] + "_ovmask" + splitext(map)[1]

def name_csv_path(map): return splitext(map)[0] + ".csv"
def boundingbox_csv_path(map): return splitext(map)[0] + "_bbox.csv"
def labelbox_csv_path(map): return splitext(map)[0] + "_lbox.csv"

def load_name_csv(map): return pd.read_csv(name_csv_path(map)).split_columns('color', '|', int)
def load_boundingbox_csv(map): return pd.read_csv(boundingbox_csv_path(map)).split_columns(('bbox', 'color'), '|', int)
def load_labelbox_csv(map): return pd.read_csv(labelbox_csv_path(map)).split_columns(('bbox', 'color'), '|', int)

def generate_name_csv(map, presorted=(), sort=ImageMapSort.HORIZONTAL, overwrite=False):
    """Generate a name csv skeleton, for use in map_chart."""
    if not overwrite and os.path.exists(name_csv_path(map)):
        raise Exception("Imagemap csv file already exists.")
    logger.info("Generating name CSV file at {}".format(name_csv_path(map)))
    img = Image.open(map)
    if sort == ImageMapSort.USAGE:
        cols = [c for _,c in sorted(img.getcolors(), reverse=True)]
    else:
        data = np.array(img)
        if sort == ImageMapSort.HORIZONTAL: data = data.transpose([1,0,2])
        coldict = OrderedDict()
        for row in data:
            for pixel in row:
                coldict[tuple(pixel)] = True
        cols = list(coldict)
    cols = list(presorted) + [c for c in cols if c not in presorted]
    rs = [{ 'color': "|".join(str(x) for x in c), 'name': "color{}".format(i) } for i,c in enumerate(cols)]
    pd.DataFrame(rs).to_csv(name_csv_path(map), index=False, encoding="utf-8")

def generate_bbox_csv(map, labels=True):
    """Generate a bounding box csv either for labels or for the map itself, for use in map_chart."""
    csv_path = labelbox_csv_path(map) if labels else boundingbox_csv_path(map)
    img = Image.open(labelbox_img_path(map) if labels else map)
    logger.info("Generating bounding box CSV file at {}".format(csv_path))
    data = np.array(img)
    xmin, xmax, ymin, ymax = {}, {}, {}, {}
    for y,row in enumerate(data):
        for x,pixel in enumerate(row):
            c = tuple(pixel)
            xmin[c] = min(xmin.get(c,img.width), x)
            xmax[c] = max(xmax.get(c,0), x)
            ymin[c] = min(ymin.get(c,img.height), y)
            ymax[c] = max(ymax.get(c,0), y)
    rs = [{ 'color': "|".join(str(x) for x in c[:3]), 'bbox': "|".join(str(x) for x in (xmin[c], ymin[c], xmax[c], ymax[c])) } for c in xmin if ImageColor.getrgba(c).alpha == 255 ]
    pd.DataFrame(rs).to_csv(csv_path, index=False, encoding="utf-8")

def generate_tile_map(array, filename, size, border=0, bg="white"):
    """Generate a grid-based map image and related files from an array of labels."""
    if isinstance(size, Integral): size = (size, size)
    labels = { l for row in array for l in row if not non(l) }
    colmap = lambda i: ((i%40)*5+(i//40), (i%40)*5+(i//40), 200-(i//100)*5)
    palette = { l : colmap(i) for i,l in enumerate(labels) }
    imgarray = [ [ None if non(l) else Image.new("RGB", size, palette[l]) for l in row ] for row in array ]
    img = Image.from_array(imgarray, bg=bg).convert("RGB")
    img.save(filename)
    names = [{ 'color': "|".join(str(x) for x in c), 'name': l } for l,c in palette.items()]
    pd.DataFrame(names).to_csv(name_csv_path(filename), index=False, encoding="utf-8")
    img.save(labelbox_img_path(filename))
    generate_bbox_csv(filename)
    
def map_chart(map, color_fn, label_fn=None, label_font=None, label_color="black", overlay_fn=None, resize_patterns=False):
    """Generate a map chart from a map image and color mapping. If present, this will use a name csv file with image names
    and a label csv file with label bounding boxes.
    - map (filename): map image filename (and template for the name and label csv filenames).
    - color_fn (name -> color/pattern/None): a dict or function that gets passed each region name (or color tuple, if there isn't one) and returns a new color, pattern, or None (to leave the region unchanged).
    - label_fn (name, width, height -> text/image/None): an dict or function that returns either a text label or image. The label location is determined from the label csv file. [None]
    - label_font (font): font to use for text labels. [None]
    - label_color (color): color to use for text labels. [black]
    - overlay_fn (name -> boolean): whether to include an overlay for a given region. [only if the region is labelled]
    - resize_patterns (boolean): whether pattern images should be resized rather than tiled. [False]
    """
    
    # read image, name and bbox csv
    img = Image.open(map)
    try:
        df = load_name_csv(map)
        logger.info("Using color name file {}".format(name_csv_path(map)))
        namemap = { tuple(d['color']) : d['name'] for _,d in df.iterrows() }
    except FileNotFoundError:
        logger.warning("No color name file found at {}".format(name_csv_path(map)))
        namemap = {}
    try:
        df = load_boundingbox_csv(map)
        bboxes = { tuple(d["color"]) : BoundingBox(d['bbox']) for _,d in df.iterrows() }
    except FileNotFoundError:
        logger.warning("No bounding box file found at {}".format(boundingbox_csv_path(map)))
        bboxes = { }
        
    # generate map
    colors = [(c,namemap.get(c, c)) for _,c in img.getcolors()]
    original = img.copy()
    for c,name in colors:
        bbox = bboxes.get(c[:3], BoundingBox(img))
        color = ignoring_extra_args(color_fn)(name, bbox.width, bbox.height) if callable(color_fn) else color_fn.get(name)
        if color is None: continue
        mask = original.select_color(c)
        if not isinstance(color, Image.Image):
            pattern = Image.new("RGBA", img.size, color)
        elif not resize_patterns:
            pattern = Image.from_pattern(color, img.size)
        else:
            pattern = color.resize((bbox.width, bbox.height)).pad((bbox.l, bbox.u, img.width - bbox.r, img.height - bbox.d), 0)
        img.place(pattern, mask=mask, copy=False)
            
    # generate labels
    labelled = set()
    if label_fn is not None:
        df = load_labelbox_csv(map)
        logger.info("Using label bounding box file {}".format(labelbox_csv_path(map)))
        labelboxes = { tuple(d["color"]) : BoundingBox(d['bbox']) for _,d in df.iterrows() }
        for c,name in colors:
            c = c[:3]
            if c not in labelboxes:
                if ignoring_extra_args(label_fn)(name, img.width, img.height) is not None:
                    logger.warning("No label location found for {}".format(name))
                continue
            label = ignoring_extra_args(label_fn)(name, labelboxes[c].width, labelboxes[c].height) if callable(label_fn) else label_fn.get(name)
            if label is None:
                continue
            if isinstance(label, str):
                label = Image.from_text(label, label_font, label_color)
            if label.width > labelboxes[c].width or label.height > labelboxes[c].height:
                logger.warning("{}x{} label for {} too small to fit {}x{} bounding box".format(label.width, label.height, name, labelboxes[c].width, labelboxes[c].height))
            else:
                labelled.add(c)
                img = img.pin(label, labelboxes[c].center)
                
    # add overlay
    if os.path.exists(overlay_img_path(map)):
        logger.info("Using overlay image file {}".format(overlay_img_path(map)))
        ov = Image.open(overlay_img_path(map))
        mask = None
        if os.path.exists(overlay_mask_img_path(map)):
            logger.info("Using overlay mask file {}".format(overlay_mask_img_path(map)))
            ovmask = Image.open(overlay_mask_img_path(map))
            mask = Image.new("1", ov.size, "black")
            overlays = labelled if overlay_fn is None else [c for c,name in colors if overlay_fn(name)]
            for c in overlays:
                cmask = ovmask.select_color(c)
                mask = mask.place(cmask, mask=cmask)
        img.overlay(ov, mask=mask)
    return img
            
