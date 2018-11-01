from os.path import splitext
from enum import Enum
from functools import reduce
from itertools import chain

from pudzu.bamboo import *
from pudzu.dates import *
from pudzu.pillar import *
    
# Random collection of Pillow-based charting functions

logger = logging.getLogger('charts')

# Legends

def generate_legend(boxes, labels, box_sizes=40, font_family=None, fg="black", bg="white",
                    header=None, footer=None, padding=(2,3), max_width=None, spacing=0, box_mask=None, border=True):
    """Generate a chart category legend.
    - boxes (list of colors/images): colors or images to use as boxes
    - labels (list of markups/images/lists): labels to use beside the boxes
    - box_sizes (int/(int,int)/list of (int,int)): size(s) of boxes to use for colors; height can be set to ... [40x40]
    - font_family (font family): font function supporting optional bold and italics parameters [None]
    - fg (color): text and border color [black]
    - bg (color): background color [white]
    - header (markup/image/None): header at top of legend, automatically bolded if markup [None]
    - footer (markup/image/None): footer at bottom of legend, automatically italicised if markup [None]
    - padding (int/(int,int)): padding around header, legend and footer
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
    if isinstance(header, str):
        if "**" not in header: header = "**{}**".format(header)
        header = Image.from_markup(header, font_family, fg=fg, bg=bg, max_width=max_width).pad(2, bg)
    if isinstance(footer, str):
        if "//" not in footer: footer = "//{}//".format(footer)
        footer = Image.from_markup(footer, font_family, fg=fg, bg=bg, max_width=max_width).pad(2, bg)
        
    if len(boxes) > 0:
        max_box_width = max(box.width if isinstance(box, Image.Image) else size[0] for box, size in zip(boxes, box_sizes))
        max_label_width = None if max_width is None else max_width - max_box_width - 8
        
        box_label_array = []
        for box, label, size in zip(boxes, labels, box_sizes):
            if isinstance(label, str):
                label = Image.from_markup(label, font_family, fg=fg, bg=bg, max_width=max_label_width).pad(2, bg)
            if not isinstance(box, Image.Image):
                box = Image.new("RGBA", (size[0], size[1] if size[1] != ... else label.height + 6), box)
            if non_string_sequence(label):
                labels = label
                label = Image.new("RGBA", box.size, bg)
                offsets = Padding(0)
                for i, l in enumerate(labels):
                    if isinstance(l, str):
                        l = Image.from_markup(l, font_family, fg=fg, bg=bg, max_width=max_label_width).pad(2, bg)
                    label = label.pin(l, (0, (box.height * i) // (len(labels) - 1)), align=(0, 0.5), bg=bg, offsets=offsets)
            box_label_array.append([box, label])
        label_img = Image.from_array(box_label_array, padding=(1,spacing), xalign=[0.5, 0], bg=bg)
        
        if box_mask is not None:
            boxes_size = (max_box_width, label_img.height - 2*spacing*len(box_label_array))
            label_img = label_img.overlay(Image.new("RGBA", boxes_size, bg), (1,spacing), mask=box_mask.resize(boxes_size).invert_mask())
    else:
        label_img = None
    
    legend = Image.from_column([i for i in [header, label_img, footer] if i is not None], padding=padding, xalign=0, bg=bg)
    
    if border: legend = legend.pad(2,bg).pad(1, fg)
    return legend
    
# Bar charts

class BarChartType(Enum):
    """Bar Chart types."""
    SIMPLE, STACKED, STACKED_PERCENTAGE, OVERLAYED = range(4)

class BarChartLabelPosition(Enum):
    """Bar Chart label position."""
    AXIS, OUTSIDE, INSIDE, ABOVE, BELOW = range(5)

def bar_chart(data, bar_width, chart_height, type=BarChartType.SIMPLE, horizontal=False, 
              fg="black", bg="white", spacing=1, group_spacing=0,
              ymin=None, ymax=None, grid_interval=None, grid_width=1, tick_interval=Ellipsis, 
              label_interval=Ellipsis, label_font=None, colors=VegaPalette10, 
              ylabels=Ellipsis, clabels=Ellipsis, rlabels=Ellipsis,
              xlabel=None, ylabel=None, title=None,
              legend_position=None, legend_fonts=None, legend_box_sizes=(40,40), legend_args={}):
    """Plot a bar chart.
    - data (pandas dataframe): table to plot
    - bar_width (int): bar width (or height, if horizontal)
    - chart_height (int): chart height (or width, if horizontal)
    - type (BarChartType): type of bar chart [BarChartType.SIMPLE]
    - horizontal (Boolean): orientation of bar chart [False]
    - fg (color): axes and font color [black]
    - bg (color): background color [white]
    - spacing (int): column spacing either side of groups [1]
    - group_spacing (int): column spacing either side of bars within a group [0]
    - ymin (float): minimum y value [auto]
    - ymax (float): maximum y value [auto]
    - grid_interval (float): grid line interval [zero line only]
    - grid_width (int): grid width in pixels [1]
    - tick_interval (float): tick line interval [grid_interval]
    - label_interval (float): y label interval [grid_interval]
    - label_font (font): font to use for text labels [none]
    - colors (col, row, value -> color/image/(size->image)): color or image to use for bars [Vega palette]
    - ylabels (format/value -> image/string): format string or image or text to use for y-axis labels [3 sig figs, or % for stacked]
    - clabels (col,row,value,(width,height) -> image/string): image or text to use for column labels; alternatively, a BarChartLabelPosition or a dict keyed by BarChartLabelPosition [value]
    - rlabels (row -> image/string): image or font to use for row labels; alternatively, a BarChartLabelPosition or a dict keyed by BarChartLabelPosition [row name]
    - xlabel (image): image to use for x axis label [none]
    - ylabel (image): image to use for y axis label [none]
    - title (image): image to use for title [none]
    - legend_position (alignment): legend alignment [None]
    - legend_fonts (font family): font family [None]
    - legend_box_sizes (col->int/(int,int)): sizes to use for legend boxes [40x40]
    - legend_args (dict): additional arguments to generate legends [none]
    Functional arguments don't need to accept all the arguments and can also be passed in as
    constants or lists instead.
    """
    
    # Arguments and defaults
    if type in [BarChartType.SIMPLE, BarChartType.OVERLAYED]:
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
      
    default_format = "{:.0%}".format if type == BarChartType.STACKED_PERCENTAGE else artial(format_float, 3)
    
    if isinstance(clabels, BarChartLabelPosition): clabels = { clabels : ... }
    if isinstance(rlabels, BarChartLabelPosition): rlabels = { rlabels : ... }
    clabel_dict = make_mapping(clabels, lambda: BarChartLabelPosition.AXIS if type == BarChartType.SIMPLE else 
                                                BarChartLabelPosition.OUTSIDE if type == BarChartType.OVERLAYED else
                                                BarChartLabelPosition.INSIDE)
    rlabel_dict = make_mapping(rlabels, lambda: BarChartLabelPosition.BELOW)
    clabel_dict = valmap((lambda v: (lambda c,r,v: default_format(v)) if v == Ellipsis else v), clabel_dict)
    rlabel_dict = valmap((lambda v: (lambda r: str(data.index[r])) if v == Ellipsis else v), rlabel_dict)
    
    if type in [BarChartType.SIMPLE, BarChartType.OVERLAYED]:
        if not all(k in [BarChartLabelPosition.ABOVE, BarChartLabelPosition.BELOW] for k in rlabel_dict.keys()):
            raise ValueError("Row labels in simple charts must above or below the chart.")
    else:
        if any(k != BarChartLabelPosition.INSIDE for k in clabel_dict.keys()):
            raise ValueError("Column labels in stacked charts must be inside the bar.")
        if not all(k in [BarChartLabelPosition.ABOVE, BarChartLabelPosition.BELOW, BarChartLabelPosition.OUTSIDE] for k in rlabel_dict.keys()):
            raise ValueError("Row labels in stacked charts must above, below or outside the bar.")
            
    if grid_interval is None:
        grid_interval = 1 if type == BarChartType.STACKED_PERCENTAGE else max(abs(ymin), ymax) * 2
    if tick_interval is Ellipsis:
        tick_interval = grid_interval
    if label_interval is Ellipsis:
        label_interval = grid_interval

    def make_fn_arg(input):
        if non_string_iterable(input): return lambda *args: input[args[0] % len(input)]
        elif not callable(input): return lambda *args: input
        else: return ignoring_extra_args(input)

    color_fn = make_fn_arg(colors)
    clabel_dict = valmap(make_fn_arg, clabel_dict)
    rlabel_dict = valmap(make_fn_arg, rlabel_dict)
    lsize_fn = make_fn_arg(legend_box_sizes)
    if legend_position: lalign = Alignment(legend_position)

    if ylabels == Ellipsis: ylabels = default_format
    ylabel_fn = ylabels if callable(ylabels) else lambda v: ylabels.format(v)

    # Helpers
    tick_size = 0 if tick_interval is None else bar_width // 4
    factor = chart_height / (ymax - ymin)
    positive_height_fn = lambda v: int(max(0, min(v, ymax) - max(0, ymin)) * factor)
    negative_height_fn = lambda v: int(max(0, min(0, ymax) - max(v, ymin)) * factor)
    y_coordinate_fn = lambda v: int(chart_height - ((v - ymin) * factor))
    bgtransparent = RGBA(bg)._replace(alpha=0)
    
    # (Horizontal charts were sort of tacked on, sorry!)
    def hzimg(img, horizontal=horizontal):
        return img.transpose(Image.ROTATE_90) if horizontal and isinstance(img, Image.Image) else img
    def hzsize(size, horizontal=horizontal):
        return tuple(reversed(size)) if horizontal else size
    def hzalign(align):
        return Alignment((align.y, (1-align.x))) if horizontal else align
    def make_box(fill, size, horizontal=horizontal):
        if callable(fill): return hzimg(fill(hzsize(size, horizontal=horizontal)), horizontal=horizontal)
        elif isinstance(fill, Image.Image): return hzimg(fill.resize(hzsize(size, horizontal=horizontal)), horizontal=horizontal)
        else: return Image.new("RGBA", size, fill)
    
    # Bars
    groups = []
    for r, row in enumerate(data.values):
        group_bars, sumv = [], 0
        for c, v in enumerate(row):
            if type == BarChartType.STACKED_PERCENTAGE:
                v = v / sum(row)
                fill = color_fn(c,r,v)
                pbar = make_box(fill, (bar_width, positive_height_fn(v+sumv)-positive_height_fn(sumv)))
                nbar = make_box(fill, (bar_width, 0))
                sumv += v
            else:
                fill = color_fn(c,r,v)
                pbar = make_box(fill, (bar_width, positive_height_fn(v)))
                nbar = make_box(fill, (bar_width, negative_height_fn(v)))
            
            def with_inside_label(bar):
                if BarChartLabelPosition.INSIDE in clabel_dict:
                    label = clabel_dict[BarChartLabelPosition.INSIDE](c,r,v,bar.width,bar.height)
                    if isinstance(label, str):
                        label = Image.from_text(label, label_font, fg=fg, align='center') if label_font else None
                    if label is not None:
                        return bar.place(hzimg(label))
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
        elif type == BarChartType.OVERLAYED:
            ordered = [bar for bar,_ in sorted(zip(group_bars, row), key=lambda p: abs(p[1]), reverse=True)]
            group = reduce(lambda img,bar: img.place(bar), ordered[1:], ordered[0])
        else:
            group = Image.from_row(group_bars, padding=(group_spacing,0), bg=bgtransparent, yalign=0)
        groups.append(group)
    chart = Image.from_row(groups, padding=(spacing,0), bg=bgtransparent, yalign=0)
    
    # Legend
    if legend_position is not None:
        boxes, labels, box_sizes = [], [], []
        for c in range(len(data.columns)):
            fill = color_fn(c,0,0)
            boxes.append(make_box(fill, lsize_fn(c), False) if callable(fill) or isinstance(fill, Image.Image) else fill)
            box_sizes.append(lsize_fn(c))
            labels.append(str(data.columns[c]))
        base_args = dict(boxes=boxes, labels=labels, box_sizes=box_sizes, font_family=legend_fonts, fg=fg, bg=bg)
        legend = generate_legend(**merge_dicts(base_args, legend_args))
        chart = chart.place(hzimg(legend.pad(10,0)), hzalign(lalign))

    # Keep track of offsets relative to chart
    offsets = Padding(0)
    
    # Grid
    chart = chart.pad((tick_size,0,0,0), bg=0, offsets=offsets)
    grid = Image.new("RGBA", (chart.width, chart.height), (255,255,255,0))
    gridcolor = RGBA(fg)._replace(alpha=80)
    griddraw = ImageDraw.Draw(grid)
    if grid_width: griddraw.line([(tick_size, y_coordinate_fn(ymin)), (tick_size, y_coordinate_fn(ymax))], fill=fg, width=grid_width)
    if grid_interval is not None:
        for i in range(ceil(ymin / grid_interval), floor(ymax / grid_interval) + 1):
            y = y_coordinate_fn(i * grid_interval)
            if grid_width: griddraw.line([(tick_size, y), (chart.width, y)], fill=fg if i == 0 else gridcolor, width=grid_width)
    if tick_interval is not None:
        for i in range(ceil(ymin / tick_interval), floor(ymax / tick_interval) + 1):
            y = y_coordinate_fn(i * tick_interval)
            if grid_width: griddraw.line([(0, y), (tick_size, y)], fill=fg, width=grid_width)
    del griddraw
    chart = Image.alpha_composite(grid, chart)
    
    # Numeric labels
    if label_interval is not None and ylabels is not None:
        for i in range(ceil(ymin / label_interval), floor(ymax / label_interval) + 1):
            y = i * label_interval
            label = ylabel_fn(y)
            if isinstance(label, str):
                label = Image.from_text(label, label_font, fg=fg) if label_font else None
            if label is not None:
                chart = chart.pin(hzimg(label), (-tick_size-10, y_coordinate_fn(y)), align=(1,0.5), bg=bg, offsets=offsets)
       
    # Column labels
    for clabels_pos, clabel_fn in clabel_dict.items():
        if clabels_pos == BarChartLabelPosition.INSIDE: continue
        for r, row in enumerate(data.values):
            for c, v in enumerate(row):
                label = clabel_fn(c,r,v)
                if isinstance(label, str):
                    label = Image.from_text(label, label_font, fg=fg, align='center', padding=hzsize((0,2)))  if label_font else None
                if label is None:
                    continue
                if type == BarChartType.SIMPLE:
                    x = (r * (len(data.columns) * (bar_width + 2 * group_spacing) + 2 * spacing) +
                         spacing + c * (bar_width + 2 * group_spacing) + group_spacing + bar_width // 2)
                else:
                    x = r * (bar_width + 2 * spacing) + spacing + bar_width // 2
                if clabels_pos == BarChartLabelPosition.AXIS:
                    y = y_coordinate_fn(0) + int(v >= 0)
                elif clabels_pos == BarChartLabelPosition.OUTSIDE:
                    y = y_coordinate_fn(v) + int(v < 0)
                elif clabels_pos == BarChartLabelPosition.ABOVE:
                    y = y_coordinate_fn(ymax) + int(v <= 0)
                elif clabels_pos == BarChartLabelPosition.BELOW:
                    y = y_coordinate_fn(ymin) + int(v <= 0)
                label_at_top = y <= y_coordinate_fn(0)
                chart = chart.pin(hzimg(label), (x, y), align=(0.5,int(label_at_top)), bg=bg, offsets=offsets)
    
    # Row labels
    old_offsets = Padding(offsets)
    for rlabels_pos, rlabel_fn in rlabel_dict.items():
        for r, row in enumerate(data.values):
            label = rlabel_fn(r)
            if isinstance(label, str):
                label = Image.from_text(label, label_font, fg=fg, align='center', padding=hzsize((0,2))) if label_font else None
            if label is None:
                continue
            if type in [BarChartType.STACKED, BarChartType.STACKED_PERCENTAGE, BarChartType.OVERLAYED]:
                x = (r * (bar_width + 2 * spacing) + (bar_width + 2 * spacing) // 2)
            else:
                x = (r * (len(data.columns) * (bar_width + 2 * group_spacing) + 2 * spacing) +
                     (len(data.columns) * (bar_width + 2 * group_spacing) + 2 * spacing) // 2)
            if rlabels_pos ==  BarChartLabelPosition.ABOVE:
                chart = chart.pin(hzimg(label), (x, -old_offsets.u), align=(0.5,1), bg=bg, offsets=offsets)
            elif rlabels_pos ==  BarChartLabelPosition.BELOW:
                chart = chart.pin(hzimg(label), (x, chart.height-offsets.y+old_offsets.d), align=(0.5,0), bg=bg, offsets=offsets)
            # TODO: support OUTSIDE rlabels in stacked mode
        
    # Background
    background = Image.new("RGBA", (chart.width, chart.height), bg)
    chart = Image.alpha_composite(background, chart)
    
    # Labels, rotation and title
    if xlabel is not None:
        chart = chart.pin(hzimg(xlabel), (int((chart.width - offsets.x)/2), chart.height - offsets.u), align=(0.5,0), bg=bg, offsets=offsets)
    if ylabel is not None:
        chart = chart.pin(hzimg(ylabel), (-offsets.l, int((chart.height - offsets.y)/2)), align=(1,0.5), bg=bg, offsets=offsets)
    if horizontal:
        chart = chart.transpose(Image.ROTATE_270)
    if title is not None:
        chart = Image.from_column((title, chart), bg=bg)
    
    return chart

# Time charts

class TimeChartLabelPosition(Enum):
    """Time Chart label position."""
    INSIDE, ABOVE, BELOW = range(3)

def time_chart(timeline_width, timeline_height,
               interval_data=None, interval_start_key="start", interval_end_key="end", interval_color_key="color", interval_label_key=None, 
               event_data=None, event_time_key="time", event_image_key=None, event_label_key=None,
               xmin=None, xmax=None, fg="white", bg="black", interval_border=1, timeline_spacing=5,
               grid_interval=None, grid_font=None, grid_labels=str, grid_label_interval=Ellipsis, 
               label_font=None, labels_left=None, labels_right=None, title=None):
    """Plot a time chart. Times can be numeric, dates or anything that supports arithmetic.
    - timeline_width (int): base width for each timeline
    - timeline_height (int): base height for each timeline
    - interval_data (pandas dataframes): one or more dataframes containing time intervals [none]
    - interval_start_key (key or series->time): start time for a given interval ["start"]
    - interval_end_key (key or series->time): end time for a given interval ["end"]
    - interval_color_key (key or series,width,height->color/image): background for a given interval ["color"]
    - interval_label_key (key or series,width,height->image/string): label for a given interval; optionally a dict keyed by TimeChartLabelPosition(s) [none]
    - event_data: (pandas dataframes): one or more dataframes containing time events [none]
    - event_time_key (key or series->time): time for a given event ["time"]
    - event_image_key (key or series,width,height->image): image for a given event [none]
    - event_label_key (key or series,width,height->image/string): label for a given event; optionally a dict keyed by TimeChartLabelPosition(s) [none]
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
    - labels_right (images/strings): timeline labels on the right [none]
    - title (image): image to use for title [none]
    Functional arguments don't need to accept all the arguments and can also be passed in as
    constants.
    """

    # arguments and defaults
    interval_data = make_sequence(interval_data)
    event_data = make_sequence(event_data)
    labels_right = make_sequence(labels_right)
    labels_left = make_sequence(labels_left)
    
    if len(interval_data) == len(event_data) == 0:
        raise ValueError("At least one of interval data and event data must be specified.")
    if len(set(len(t) for t in (interval_data, event_data, labels_right, labels_left) if len(t) > 0)) != 1:
        raise ValueError("Interval data, event data and timeline labels must have the same length if specified")
        
    def make_key_arg(key):
        if callable(key): return key
        elif isinstance(key, str): return lambda d: get_non(d, key)
        else: return lambda : key
    
    interval_start_fn = make_key_arg(interval_start_key)
    interval_end_fn = make_key_arg(interval_end_key)
    interval_color_fn = make_key_arg(interval_color_key)
    interval_labels_dict = make_mapping(interval_label_key, lambda: TimeChartLabelPosition.INSIDE)
    interval_labels_dict = { frozenset(make_iterable(k)): make_key_arg(v) for k,v in interval_labels_dict.items() }
    event_time_fn = make_key_arg(event_time_key)
    event_image_fn = make_key_arg(event_image_key)
    event_labels_dict = make_mapping(event_label_key, lambda: TimeChartLabelPosition.INSIDE)
    event_labels_dict = { frozenset(make_iterable(k)): make_key_arg(v) for k,v in event_labels_dict.items() }
    grid_label_fn = grid_labels if callable(grid_labels) else lambda v: grid_labels
    
    if xmin is None:
        xmin = min(fn(d) for fn, data in ((interval_start_fn, interval_data), (event_time_fn, event_data)) for df in data for _,d in df.iterrows())
    if xmax is None:
        xmax = max(fn(d) for fn, data in ((interval_end_fn, interval_data), (event_time_fn, event_data)) for df in data for _,d in df.iterrows())
    if xmin >= xmax:
        raise ValueError("Mininum x value {} must be smaller than maximum x vaue {}".format(xmin, xmax))
    def xvalue(x):
        return int((x - xmin) / (xmax - xmin) * timeline_width)
    if grid_interval is None:
        grid_interval = xmax-xmin
    if grid_label_interval is Ellipsis:
        grid_label_interval = grid_interval
    
    # chart
    logger.info("Generating time chart")
    timelines, llabels, rlabels, toffsets = [], [], [], []
    for intervals, events, llabel, rlabel in zip_longest(interval_data, event_data, labels_left, labels_right):
        timeline = Image.new("RGBA", (timeline_width, timeline_height), bg)
        offsets = Padding(0)
        
        if intervals is not None:
            nextpos = { pos: None for pos in interval_labels_dict }
            for _,d in intervals.iterrows():
                start, end = interval_start_fn(d), interval_end_fn(d)
                if end < xmin or start > xmax: continue
                start, end = xvalue(clip(start, xmin, xmax)), xvalue(clip(end, xmin, xmax))
                w, h = end-start, timeline_height
                color = ignoring_extra_args(interval_color_fn)(d, w, h)
                bar = Image.from_pattern(color, (w, h)) if isinstance(color, Image.Image) else Image.new("RGBA", (w, h), color)
                bar = bar.trim((interval_border,0,0,0)).pad((interval_border,0),bg)
                timeline.overlay(bar, (start+offsets.l, offsets.u))
                for pos, label_fn in interval_labels_dict.items():
                    img = ignoring_extra_args(label_fn)(d, bar.width, bar.height)
                    if img is None: continue
                    if isinstance(img, str):
                        img = Image.from_text(img, label_font, fg=fg, padding=2)
                    if TimeChartLabelPosition.INSIDE in pos and img.width < (bar.width - 3) and img.height < bar.height:
                        timeline = timeline.pin(img, ((start+end)//2, timeline_height//2), bg=bg, offsets=offsets)
                    elif TimeChartLabelPosition.ABOVE in pos and nextpos[pos] != TimeChartLabelPosition.BELOW:
                        timeline = timeline.pin(img, ((start+end)//2, 0), align=(0.5,1), bg=bg, offsets=offsets)
                        if TimeChartLabelPosition.BELOW in pos: nextpos[pos] = TimeChartLabelPosition.BELOW
                    elif TimeChartLabelPosition.BELOW in pos:
                        timeline = timeline.pin(img, ((start+end)//2, timeline_height), align=(0.5,0), bg=bg, offsets=offsets)
                        if TimeChartLabelPosition.ABOVE in pos: nextpos[pos] = TimeChartLabelPosition.ABOVE
                        
        if events is not None:
            nextpos = { pos: None for pos in event_labels_dict }
            for _,d in events.iterrows():
                middle = event_time_fn(d)
                if middle < xmin or middle > xmax: continue
                middle = xvalue(middle)
                event_img = ignoring_extra_args(event_image_fn)(d, w, h) or Image.EMPTY_IMAGE
                timeline = timeline.pin(event_img, (middle, timeline_height/2), bg=bg, offsets=offsets)
                for pos, label_fn in event_labels_dict.items():
                    img = ignoring_extra_args(label_fn)(d, event_img.width, event_img.height)
                    if img is None: continue
                    if isinstance(img, str):
                        img = Image.from_text(img, label_font, fg=fg, padding=2)
                    if TimeChartLabelPosition.INSIDE in pos and img.width < event_img.width and img.height < event_img.height:
                        timeline = timeline.pin(img, (middle, timeline_height//2), bg=bg, offsets=offsets)
                    elif TimeChartLabelPosition.ABOVE in pos and nextpos[pos] != TimeChartLabelPosition.BELOW:
                        timeline = timeline.pin(img, (middle, min(0, (timeline_height - event_img.height) // 2)), align=(0.5,1), bg=bg, offsets=offsets)
                        if TimeChartLabelPosition.BELOW in pos: nextpos[pos] = TimeChartLabelPosition.BELOW
                    elif TimeChartLabelPosition.BELOW in pos:
                        timeline = timeline.pin(img, (middle, max(timeline_height, (timeline_height + event_img.height) // 2)), align=(0.5,0), bg=bg, offsets=offsets)
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
    chart = Image.from_array(array, padding=(4,timeline_spacing), bg=bg, xalign=xalign)
    
    # grid
    logger.info("Generating time chart grid and labels")
    xoffset = maxoffset + 4 + (max(label.width for label in llabels)+4*2 if llabels else 0)
    grid = Image.new("RGBA", (chart.width, chart.height), (255,255,255,0))
    gridcolor = RGBA(fg)._replace(alpha=127)
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

class GridChartLabelPosition(Enum):
    """Grid Chart label position."""
    BEFORE, AFTER = range(2)
    TOP, BOTTOM = range(2)
    LEFT, RIGHT = range(2)

def grid_chart(data, cell=lambda v: str(v), group=None,
               fg="white", bg="black", xalign=0.5, yalign=0.5, padding=(0,0,0,0), 
               group_fg_colors=tuple(VegaPalette10), group_bg_colors=lambda _,c: c._replace(alpha=128), group_bg_patterns=None,
               group_border=2, group_padding=(0,0,0,0), group_rounded=True,
               row_label=Ellipsis, col_label=Ellipsis, label_font=None, group_label=None, title=None):
    """Plot an image grid chart with optional Venn-like groupings.
    - data (pandas dataframe): table to base chart on
    - cell (datavalue,row,column->image/None): content of each grid cell [None]
    - group (datavalue,row,column->groups/None): optional group of each grid cell [None]
    - fg (color): font color [white]
    - bg (color): background color [black]
    - xalign (0 to 1, or triple): cell x alignment, or three alignments for left labels, cells and right labels [center]
    - yalign (0 to 1, or triple): cell y alignment, or three alignments for top labels, cells and bottom labels [center]
    - padding (Padding): cell padding [0]
    - group_fg_colors (group->color): dict or function of groups to fg colors, or sequence of colors [VegaPalette10]
    - group_bg_colors (group,[fg color]->color): dict or function of groups to bg colors, or sequence of colors; None to use fg [fg colors with 128 opacity]
    - group_bg_patterns (groups,[bg colors]->color/pattern): function of group combinations to bg patterns or colors; None to use bg color combinations from above [None]
      **IMPLEMENTATION NOTE**: this currently relies on each group combination starting with a unique default bg color based on group_bg_colors
    - group_border (int): grouping border [2]
    - group_padding (Padding): group edge padding [0]
    - group_rounded (Boolean): round group edges [True]
    - row_label (row, rowvalues -> image/string): image or string for row labels; optionally a dict keyed by GridChartLabelPosition [row name]
    - col_label (col, colvalues -> image/string): image or string for column labels; optionally a dict keyed by GridChartLabelPosition [column name]
    - label_font (font): font to use for text labels [none]
    - title (image): image to use for title [none]
    Functional arguments don't need to accept all the arguments and can also be passed in as
    constants.
    """
    
    padding = Padding(padding)
    gp = Padding(group_padding)
    tbg = RGBA(bg)._replace(alpha=0)
    
    cell_fn = ignoring_extra_args(cell) if callable(cell) else lambda v, r, c: cell
    group_fn = ignoring_extra_args(group) if callable(group) else lambda v, r, c: group
    
    if isinstance(col_label, GridChartLabelPosition): col_label = { col_label : ... }
    if isinstance(row_label, GridChartLabelPosition): row_label = { row_label : ... }
    clabel_dict = make_mapping(col_label, lambda: GridChartLabelPosition.TOP)
    rlabel_dict = make_mapping(row_label, lambda: GridChartLabelPosition.LEFT)
    clabel_dict = valmap((lambda v: (lambda c,vs: str(data.columns[c])) if v == Ellipsis else v), clabel_dict)
    rlabel_dict = valmap((lambda v: (lambda r,vs: str(data.index[r])) if v == Ellipsis else v), rlabel_dict)
    clabel_dict = valmap((lambda v: ignoring_extra_args(v if callable(v) else lambda: v)), clabel_dict)
    rlabel_dict = valmap((lambda v: ignoring_extra_args(v if callable(v) else lambda: v)), rlabel_dict)
    
    xalign = [xalign] * 3 if isinstance(xalign, Real) else xalign
    if not (non_string_sequence(xalign, Real) and len(xalign) == 3):
        raise ValueError("xalign argument expected one or three alignment values, got: {}".format(xalign))
    yalign = [yalign] * 3 if isinstance(yalign, Real) else yalign
    if not (non_string_sequence(yalign, Real) and len(yalign) == 3):
        raise ValueError("yalign argument expected one or three alignment values, got: {}".format(yalign))
    
    img_array = [[cell_fn(v, r, c) for c, v in enumerate(row)] for r, row in enumerate(data.values)]
    img_array = tmap_leafs(lambda s: s if isinstance(s, Image.Image) else Image.from_text(s, label_font, fg=fg, bg=bg, padding=2) if label_font and s else None, img_array, base_factory=list)
    img_heights = [max(img.height if img is not None else 0 for img in row) + padding.y for row in img_array]
    img_widths = [max(img.width if img is not None else 0 for img in column) + padding.x for column in zip_longest(*img_array)]

    group_array = [[remove_duplicates(make_sequence(group_fn(v, r, c))) for c, v in enumerate(row)] for r, row in enumerate(data.values)]
    groups = remove_duplicates(generate_leafs(group_array))
    group_fg_col_fn = (group_fg_colors if callable(group_fg_colors) else 
                       (lambda g: group_fg_colors[g]) if isinstance(group_fg_colors, Mapping) else
                       (lambda g: group_fg_colors[groups.index(g)]) if non_string_sequence(group_fg_colors) else
                       (lambda g: group_fg_colors))
    group_bg_col_fn = (group_fg_col_fn if group_bg_colors is None else
                       (lambda g: ignoring_extra_args(group_bg_colors)(g, RGBA(group_fg_col_fn(g)))) if callable(group_bg_colors) else
                       (lambda g: group_bg_colors[g]) if isinstance(group_bg_colors, Mapping) else
                       (lambda g: group_bg_colors[groups.index(g)]) if non_string_sequence(group_bg_colors) else
                       (lambda g: group_bg_colors))
                    
    def group_cmp(group, *same, diff=()):
        return (all(0<=r<len(img_heights) and 0<=c<len(img_widths) and group in group_array[r][c] for r,c in same) and
                not any(0<=r<len(img_heights) and 0<=c<len(img_widths) and group in group_array[r][c] for r,c in diff))
             
    def OuterCorner(size, fg, bg, bcol, bwidth=group_border):
        if bwidth == 0: return Quadrant(size, fg, bg)
        if size[0] <= bwidth or size[1] <= bwidth: return Quadrant(size, bcol, bg)
        size2 = (size[0]-bwidth, size[1]-bwidth)
        bg_img = Quadrant(size, fg, bg)
        border_img = MaskIntersection(size, bcol, bcol._replace(alpha=0), masks=[Quadrant(size), Quadrant(size2).pad((bwidth, bwidth, 0, 0), 0).invert_mask()])
        return bg_img.place(border_img)
    
    def InnerCorner(size, fg, bg, bcol, bwidth=group_border):
        if bwidth == 0: return Quadrant(size, fg, bg, invert=True)
        size2 = (size[0]+bwidth, size[1]+bwidth)
        bg_img = Quadrant(size, fg, bg, invert=True).pad((bwidth, bwidth, 0, 0), fg)
        border_img = MaskIntersection(size2, bcol, bcol._replace(alpha=0), masks=[Quadrant(size2), Quadrant(size, invert=True).pad((bwidth, bwidth, 0, 0), "white")])
        return bg_img.place(border_img)
    
    euler_array = tmap_leafs(lambda _: None, img_array, base_factory=list)
    euler_bgs = {}
    for r, row in enumerate(data.values):
        for c, v in enumerate(row):
        
            # image array
            base = Image.new("RGBA", (img_widths[c], img_heights[r]), tbg)
            if img_array[r][c]:
                base.place(img_array[r][c], align=(xalign[1],yalign[1]), copy=False)
            img_array[r][c] = base
        
            # euler array (what an unholy mess! could use some serious refactoring)
            if groups:
                euler = Image.new("RGBA", (img_widths[c], img_heights[r]), tbg)
                for g in group_array[r][c]:
                    cfg = RGBA(group_fg_col_fn(g))
                    cbg = RGBA(group_bg_col_fn(g))
                    
                    mid = Rectangle((img_widths[c]-gp.x, img_heights[r]-gp.y), cbg)
                    if group_border and group_cmp(g,diff=[(r,c-1)]):
                        mid.place(Rectangle((group_border, img_heights[r]), cfg), align=0, copy=False)
                    if group_border and group_cmp(g,diff=[(r,c+1)]):
                        mid.place(Rectangle((group_border, img_heights[r]), cfg), align=1, copy=False)
                    if group_border and group_cmp(g,diff=[(r-1,c)]):
                        mid.place(Rectangle((img_widths[c], group_border), cfg), align=0, copy=False)
                    if group_border and group_cmp(g,diff=[(r+1,c)]):
                        mid.place(Rectangle((img_widths[c], group_border), cfg), align=1, copy=False)
                    if not group_rounded and group_cmp(g,(r-1,c),(r,c-1),diff=[(r-1,c-1)]):
                        mid.place(Rectangle((group_border, group_border), cfg), align=(0,0), copy=False)
                    if not group_rounded and group_cmp(g,(r-1,c),(r,c+1),diff=[(r-1,c+1)]):
                        mid.place(Rectangle((group_border, group_border), cfg), align=(1,0), copy=False)
                    if not group_rounded and group_cmp(g,(r+1,c),(r,c-1),diff=[(r+1,c-1)]):
                        mid.place(Rectangle((group_border, group_border), cfg), align=(0,1), copy=False)
                    if not group_rounded and group_cmp(g,(r+1,c),(r,c+1),diff=[(r+1,c+1)]):
                        mid.place(Rectangle((group_border, group_border), cfg), align=(1,1), copy=False)
                    if group_rounded and group_cmp(g,diff=[(r-1,c),(r,c-1)]):
                        mid.paste(OuterCorner((gp.r, gp.d), cbg, tbg, cfg), (0,0))
                    if group_rounded and group_cmp(g,diff=[(r-1,c),(r,c+1)]):
                        mid.paste(OuterCorner((gp.l, gp.d), cbg, tbg, cfg).transpose(Image.FLIP_LEFT_RIGHT), (mid.width-gp.l,0))
                    if group_rounded and group_cmp(g,diff=[(r+1,c),(r,c-1)]):
                        mid.paste(OuterCorner((gp.r, gp.u), cbg, tbg, cfg).transpose(Image.FLIP_TOP_BOTTOM), (0,mid.height-gp.u))
                    if group_rounded and group_cmp(g,diff=[(r+1,c),(r,c+1)]):
                        mid.paste(OuterCorner((gp.l, gp.u), cbg, tbg, cfg).transpose(Image.ROTATE_180), (mid.width-gp.l,mid.height-gp.u))
                    
                    top = Rectangle((img_widths[c]-gp.x, gp.u), cbg if group_cmp(g,(r-1,c)) else tbg)
                    if group_border and (group_cmp(g, (r-1,c), diff=[(r,c-1)]) or group_cmp(g, (r-1,c), diff=[(r-1,c-1)])):
                        top.place(Rectangle((group_border, gp.u), cfg), align=0, copy=False)
                    if group_border and (group_cmp(g, (r-1,c), diff=[(r,c+1)]) or group_cmp(g, (r-1,c), diff=[(r-1,c+1)])):
                        top.place(Rectangle((group_border, gp.u), cfg), align=1, copy=False)
                    
                    bottom = Rectangle((img_widths[c]-gp.x, gp.d), cbg if group_cmp(g,(r+1,c)) else tbg)
                    if group_border and (group_cmp(g, (r+1,c), diff=[(r,c-1)]) or group_cmp(g, (r+1,c), diff=[(r+1,c-1)])):
                        bottom.place(Rectangle((group_border, gp.d), cfg), align=0, copy=False)
                    if group_border and (group_cmp(g, (r+1,c), diff=[(r,c+1)]) or group_cmp(g, (r+1,c), diff=[(r+1,c+1)])):
                        bottom.place(Rectangle((group_border, gp.d), cfg), align=1, copy=False)
                    
                    left = Rectangle((gp.l, img_heights[r]-gp.y), cbg if group_cmp(g,(r,c-1)) else tbg)
                    if group_border and (group_cmp(g, (r,c-1), diff=[(r-1,c)]) or group_cmp(g, (r,c-1), diff=[(r-1,c-1)])):
                        left.place(Rectangle((gp.l, group_border), cfg), align=0, copy=False)
                    if group_border and (group_cmp(g, (r,c-1), diff=[(r+1,c)]) or group_cmp(g, (r,c-1), diff=[(r+1,c-1)])):
                        left.place(Rectangle((gp.l, group_border), cfg), align=1, copy=False)
                    
                    right = Rectangle((gp.r, img_heights[r]-gp.y), cbg if group_cmp(g,(r,c+1)) else tbg)
                    if group_border and (group_cmp(g, (r,c+1), diff=[(r-1,c)]) or group_cmp(g, (r,c+1), diff=[(r-1,c+1)])):
                        right.place(Rectangle((gp.r, group_border), cfg), align=0, copy=False)
                    if group_border and (group_cmp(g, (r,c+1), diff=[(r+1,c)]) or group_cmp(g, (r,c+1), diff=[(r+1,c+1)])):
                        right.place(Rectangle((gp.r, group_border), cfg), align=1, copy=False)
                    
                    top_left = Rectangle((gp.l, gp.u), cbg if group_cmp(g,(r-1,c),(r,c-1),(r-1,c-1)) else tbg)
                    top_right = Rectangle((gp.r, gp.u), cbg if group_cmp(g,(r-1,c),(r,c+1),(r-1,c+1)) else tbg)
                    bottom_left = Rectangle((gp.l, gp.d), cbg if group_cmp(g,(r+1,c),(r,c-1),(r+1,c-1)) else tbg)
                    bottom_right = Rectangle((gp.r, gp.d), cbg if group_cmp(g,(r+1,c),(r,c+1),(r+1,c+1)) else tbg)
                    
                    img = Image.from_array([[top_left, top, top_right],[left,mid,right],[bottom_left,bottom,bottom_right]])
                    
                    if group_rounded and group_cmp(g,(r-1,c),(r,c-1),diff=[(r-1,c-1)]):
                        img.paste(InnerCorner((gp.l, gp.u), cbg, tbg, cfg).transpose(Image.ROTATE_180), (0,0))
                    if group_rounded and group_cmp(g,(r-1,c),(r,c+1),diff=[(r-1,c+1)]):
                        img.paste(InnerCorner((gp.r, gp.u), cbg, tbg, cfg).transpose(Image.FLIP_TOP_BOTTOM), (img.width-gp.r-group_border,0))
                    if group_rounded and group_cmp(g,(r+1,c),(r,c-1),diff=[(r+1,c-1)]):
                        img.paste(InnerCorner((gp.l, gp.d), cbg, tbg, cfg).transpose(Image.FLIP_LEFT_RIGHT), (0,img.height-gp.d-group_border))
                    if group_rounded and group_cmp(g,(r+1,c),(r,c+1),diff=[(r+1,c+1)]):
                        img.paste(InnerCorner((gp.r, gp.d), cbg, tbg, cfg), (img.width-gp.r-group_border,img.height-gp.d-group_border))
                        
                    euler.place(img, copy=False)

                euler_array[r][c] = euler
                # should be able to recalculate the combined bg color directly but pillow isn't very consistent with alpha compositing
                euler_bgs[group_array[r][c]] = RGBA(max(euler.getcolors(euler.width * euler.height))[1])

    for rlabel_pos, rlabel_fn in rlabel_dict.items():
        for r, row in enumerate(data.values):
            label = rlabel_fn(r, list(row))
            if isinstance(label, str):
                label = Image.from_text(label, label_font, fg=fg, bg=bg, padding=(10,0)) if label_font else None
            if label is not None:
                label = label.pad(padding, bg=bg)
            if groups:
                empty_label = label and Rectangle(label.size, tbg)
            if rlabel_pos == GridChartLabelPosition.LEFT:
                img_array[r].insert(0, label)
                if groups: euler_array[r].insert(0, empty_label)
            else:
                img_array[r].append(label)
                if groups: euler_array[r].append(empty_label)
            
    for clabel_pos, clabel_fn in clabel_dict.items():
        col_labels = [None] * int(GridChartLabelPosition.LEFT in rlabel_dict)
        for c, col in enumerate(data.values.transpose()):
            label = clabel_fn(c, list(col))
            if isinstance(label, str):
                label = Image.from_text(label, label_font, fg=fg, bg=bg, padding=(0,10)) if label_font else None
            if label is not None:
                label = label.pad(padding, bg=bg)
            col_labels.append(label)
        if groups: 
            empty_labels = [ label and Rectangle(label.size, tbg) for label in col_labels ]
        if clabel_pos == GridChartLabelPosition.TOP:
            img_array.insert(0, col_labels)
            if groups: euler_array.insert(0, empty_labels)
        else:
            img_array.append(col_labels)
            if groups: euler_array.append(empty_labels)

    xaligns = [xalign[1]] * len(img_array[0])
    if GridChartLabelPosition.LEFT in rlabel_dict: xaligns[0] = xalign[0]
    if GridChartLabelPosition.RIGHT in rlabel_dict: xaligns[-1] = xalign[-1]
    yaligns = [yalign[1]] * len(img_array)
    if GridChartLabelPosition.TOP in clabel_dict: yaligns[0] = yalign[0]
    if GridChartLabelPosition.BOTTOM in clabel_dict: yaligns[-1] = yalign[-1]
    chart = Image.from_array(img_array, xalign=xaligns, yalign=yaligns, bg=tbg)
    
    if groups: 
        euler = Image.from_array(euler_array, xalign=xaligns, yalign=yaligns, bg=tbg)
        if group_bg_patterns:
            group_combos = [combo for row in group_array for combo in row]
            group_patterns = { euler_bgs[groups]: group_patterns
                               for groups in group_combos if groups
                               for group_colors in [[RGBA(group_bg_col_fn(g)) for g in groups]]
                               for group_patterns in [ignoring_extra_args(group_bg_patterns)(groups, group_colors)] if group_patterns is not None }
            euler = euler.replace_colors(group_patterns)
        chart = euler.place(chart)
        
    return Image.from_column([img for img in (title, chart) if img], bg=bg)
        
# Map charts

def name_csv_path(map): return splitext(map)[0] + ".csv"
def boundingbox_csv_path(map): return splitext(map)[0] + "_bbox.csv"
def labelbox_img_path(map): return splitext(map)[0] + "_lbox" + splitext(map)[1]
def labelbox_csv_path(map): return splitext(map)[0] + "_lbox.csv"
def overlay_img_path(map): return splitext(map)[0] + "_ov" + splitext(map)[1]
def overlay_mask_img_path(map): return splitext(map)[0] + "_ovmask" + splitext(map)[1]

def load_name_csv(map): return pd.read_csv(name_csv_path(map)).split_columns('color', '|', int)
def load_boundingbox_csv(map): return pd.read_csv(boundingbox_csv_path(map)).split_columns(('bbox', 'color'), '|', int)
def load_labelbox_csv(map): return pd.read_csv(labelbox_csv_path(map)).split_columns(('bbox', 'color'), '|', int)

class ImageMapSort(Enum):
    """Image map color sort in name CSV file."""
    USAGE, HORIZONTAL, VERTICAL = range(3)
    
def generate_name_csv(map, presorted=(), sort=ImageMapSort.HORIZONTAL, overwrite=False):
    """Generate a name csv skeleton, for use in map_chart."""
    if not overwrite and os.path.exists(name_csv_path(map)):
        raise Exception("Name csv file already exists.")
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
    rs = [{ 'color': "|".join(str(x) for x in c), 'name': "color{}".format(i), 'label_align': "" } for i,c in enumerate(cols)]
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
    rs = [{ 'color': "|".join(str(x) for x in c[:3]), 'bbox': "|".join(str(x) for x in (xmin[c], ymin[c], xmax[c], ymax[c])) } for c in xmin if RGBA(c).alpha == 255 ]
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
    
# TODO: speed up color replacements
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
        labelaligns = { tuple(d['color'])[:3] : unmake_sequence(tmap(float, str(get_non(d, 'label_align', "0.5")).split("|"))) for _,d in df.iterrows() }
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
        logger.debug("Filling {} with {}".format(name, color))
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
                label = Rectangle(labelboxes[c].size, None).place(label, align=labelaligns[c])
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
            
# Calendar charts

def month_chart(month, fonts, cell_width=60, cell_height=40, cell_padding=1, fg="black",
                day_bg="white", day_label="{D}", day_overlay=None, day_start=0,
                out_of_month_bg="white", out_of_month_label=None, out_of_month_overlay=None,
                weekday_height=20, weekday_bg="#A0A0A0", weekday_label=lambda d: d.date_format("{W}")[:3].upper(), weekday_overlay=None,
                month_height=30, month_bg="#606060", month_label="{M} {Y}", month_overlay=None, month_image=None):
    """Generate a calendar chart for a single month.
    - month (Date/DateRange): date and calendar of the month to chart
    - fonts (font/three fonts/font function): month, weekday and daily label fonts
    - cell_width (int): width of each day cell [60]
    - cell_height (int): height of each day cell [40]
    - cell_padding (int): padding between cells [1]
    - fg (color): color for labels and padding [black]
    - day_bg (date,width,height->color/pattern): day cell background [white]
    - day_label (format / date,width,height->string/img): day label ["1", "2", etc]
    - day_overlay (date,width,height->img): day overlay [None]
    - day_start (int/string): day number or name to start the week [0]
    - out_of_month_bg (date,width,height->color/pattern): out-of-month cell background [white]
    - out_of_month_label (format / date,width,height->string/img): out-of-month cell label [None]
    - out_of_month_overlay (date,width,height->img): out-of-month cell overlay [None]
    - weekday_height (int): height of each weekday cell [20]
    - weekday_bg (date,width,height->color/pattern): weekday cell background [#A0A0A0]
    - weekday_label (format / date,width,height->string/img): weekday label ["MON", "TUE", etc]
    - weekday_overlay (date,width,height->img): weekday overlay [None]
    - month_height (int): height of month cell [30]
    - month_bg (date,width,height->color/pattern): month cell background [#606060]
    - month_label (format / date,width,height->string/img): month label ["December 2017", etc]
    - month_overlay (date,width,height->img): month overlay [None]
    - month_image (image): optional month image [None]
    Functional arguments don't need to accept all the arguments and can also be passed in as
    constants.
    """
           
    # Arguments and defaults
    if month_height == Ellipsis: month_height = cell_height
    if weekday_height == Ellipsis: weekday_height = cell_height
    if out_of_month_bg == Ellipsis: out_of_month_bg = day_bg
    if out_of_month_label == Ellipsis: out_of_month_label = day_label
    if out_of_month_overlay == Ellipsis: out_of_month_overlay = day_overlay
    
    if callable(fonts): fonts = [fonts(bold=True), fonts(italics=True), fonts()]
    elif isinstance(fonts, ImageFont.FreeTypeFont): fonts = [fonts]*3
    padding = (cell_padding, cell_padding, 0, 0)
    
    def make_fn(overlay): return ignoring_extra_args(overlay if callable(overlay) else (lambda d: overlay))
    day_bg_fn = make_fn(day_bg)
    day_overlay_fn = make_fn(day_overlay)
    out_of_month_bg_fn = make_fn(out_of_month_bg)
    out_of_month_overlay_fn = make_fn(out_of_month_overlay)
    weekday_bg_fn = make_fn(weekday_bg)
    weekday_overlay_fn = make_fn(weekday_overlay)
    month_bg_fn = make_fn(month_bg)
    month_overlay_fn = make_fn(month_overlay)
    
    def make_label_fn(label): return ignoring_extra_args(label if callable(label) else (lambda d: d.date_format(label)) if isinstance(label, str) else (lambda d: label))
    day_label_fn = make_label_fn(day_label)
    out_of_month_label_fn = make_label_fn(out_of_month_label)
    weekday_label_fn = make_label_fn(weekday_label)
    month_label_fn = make_label_fn(month_label)
    
    if isinstance(month, DateRange):
        start = ApproximateDate(month.start, DatePrecision.MONTH, calendar=month.calendar)
        end = ApproximateDate(month.end, DatePrecision.MONTH, calendar=month.calendar)
        if (start != end):
            raise ValueError("Expected one-month date, got range including {} and {}".format(start, end))
        month = start
    else:
        month = ApproximateDate(month, DatePrecision.MONTH, calendar=month.calendar)
        
    if isinstance(day_start, str): day_start = month.calendar.WEEKDAYS.index(day_start)
    week_length = len(month.calendar.WEEKDAYS)
    total_width = week_length * (cell_width + cell_padding) + cell_padding
    first_day = month.start + 1 - DateFilter(lambda d: d.weekday == day_start)
    last_day = month.end + DateFilter(lambda d: d.weekday == day_start) - 1
    fullrange = DateRange(first_day, last_day, calendar=month.calendar)
    
    # Generate month calendar
    month_width = total_width-2*cell_padding
    fnargs = (month.start, month_width, month_height)
    month_bg, month_label, month_overlay = month_bg_fn(*fnargs), month_label_fn(*fnargs), month_overlay_fn(*fnargs)
    month_img = Image.from_pattern(month_bg, (month_width, month_height)) if isinstance(month_bg, Image.Image) else Image.new("RGBA", (month_width, month_height), month_bg)
    if isinstance(month_label, str): month_label = Image.from_text(month_label, fonts[0], fg)
    if month_label: month_img = month_img.place(month_label)
    if month_overlay: month_img = month_img.place(month_overlay)
    month_img = month_img.pad(padding, fg)
    
    day_imgs = []
    if weekday_height:
        weekday_imgs = []
        for day in itertools.islice(fullrange, week_length):
            if day not in month: day += DateFilter(lambda d: d.weekday == day.weekday and d in month)
            fnargs = (day, cell_width, weekday_height)
            weekday_bg, weekday_label, weekday_overlay = weekday_bg_fn(*fnargs), weekday_label_fn(*fnargs), weekday_overlay_fn(*fnargs)
            weekday_img = Image.from_pattern(weekday_bg, (cell_width, weekday_height)) if isinstance(weekday_bg, Image.Image) else Image.new("RGBA", (cell_width, weekday_height), weekday_bg)
            if isinstance(weekday_label, str): weekday_label = Image.from_text(weekday_label, fonts[1], fg)
            if weekday_label: weekday_img = weekday_img.place(weekday_label)
            if weekday_overlay: weekday_img = weekday_img.place(weekday_overlay)
            weekday_img = weekday_img.pad(padding, fg)
            weekday_imgs.append(weekday_img)
        day_imgs.append(weekday_imgs)
            
    for week in generate_batches(fullrange, week_length):
        week_imgs = []
        for day in week:
            if day in month: bg_fn, label_fn, overlay_fn = day_bg_fn, day_label_fn, day_overlay_fn
            else: bg_fn, label_fn, overlay_fn = out_of_month_bg_fn, out_of_month_label_fn, out_of_month_overlay_fn
            fnargs = (day, cell_width, cell_height)
            bg, label, overlay = bg_fn(*fnargs), label_fn(*fnargs), overlay_fn(*fnargs)
            day_img = Image.from_pattern(bg, (cell_width, cell_height)) if isinstance(bg, Image.Image) else Image.new("RGBA", (cell_width, cell_height), bg) 
            if isinstance(label, str): label = Image.from_text(label, fonts[2], fg)
            if label: day_img = day_img.place(label)
            if overlay: day_img = day_img.place(overlay)
            day_img = day_img.pad(padding, fg)
            week_imgs.append(day_img)
        day_imgs.append(week_imgs)
    grid_img = Image.from_array(day_imgs)
    
    month_image = month_image.resize_fixed_aspect(width=month_width).pad(padding, fg) if month_image else Image.EMPTY_IMAGE
    calendar_img = Image.from_column([month_img, month_image, grid_img], xalign=0).pad(padding[::-1], fg)
    return calendar_img
