from bamboo import *
from pillar import *
from os.path import splitext
from enum import Enum

# Random collection of Pillow-based charting functions

logger = logging.getLogger('charts')

# Bar charts

VEGA_PALETTE = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]

class BarChartType(Enum):
    """Bar Chart types."""
    SIMPLE, STACKED, STACKED_PERCENTAGE = range(3)

class BarChartLabelPosition(Enum):
    """Bar Chart label position."""
    AXIS, BAR, TOP, BOTTOM = range(4)

def bar_chart(data, bar_width, chart_height, type=BarChartType.SIMPLE,
              fg="black", bg="white", spacing=0, group_spacing=0,
              ymin=None, ymax=None, grid_interval=None,
              tick_interval=Ellipsis, label_interval=Ellipsis, ylabels=None, yformat=None, 
              colors=VEGA_PALETTE, clabels=None, clabels_pos=BarChartLabelPosition.AXIS, rlabels=None, rlabels_pos=BarChartLabelPosition.BOTTOM, 
              xlabel=None, ylabel=None, title=None,
              legend_position=(1,0), legend_labels=None, legend_box=None, legend_colors=None):
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
    - colors (col, row, value -> color/image/size->image): color or image to use for bars [Vega palette]
    - clabels (col, row, value -> image/font): image or font to use for column labels [none]
    - clabels_pos (BarChartLabelPosition): where to place column labels for non-stacked charts [BarChartLabelPosition.AXIS]
    - rlabels (row -> image/font): image or font to use for row labels [none]
    - rlabels_pos (BarChartLabelPosition): where to place row labels [BarChartLabelPosition.BOTTOM]
    - xlabel (image): image to use for x axis label [none]
    - ylabel (image): image to use for y axis label [none]
    - title (image): image to use for title [none]
    - legend_position (alignment): legend alignment [top-right]
    - legend_labels (col->font/image): font or image to use for legend labels [none]
    - legend_box (col->size/image): size or mask to use for legend boxes [none]
    - legend_colors (col->color/image/size->image): color or image to use for legend boxes [colors]
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
    rlabel_fn = make_fn_arg(rlabels)
    clabel_fn = make_fn_arg(clabels)
    ylabel_fn = make_fn_arg(ylabels)
    
    llabel_fn = make_fn_arg(legend_labels)
    lbox_fn = make_fn_arg(legend_box)
    lalign = Alignment(legend_position)
    lcolor_fn = (lambda c: color_fn(c,0,0)) if legend_colors is None else make_fn_arg(legend_colors)

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
    
    # Bars
    groups = []
    for r, row in enumerate(data.values):
        group_bars = []
        for c, v in enumerate(row):
            if type == BarChartType.STACKED_PERCENTAGE:
                v = v / sum(row)
            fill = color_fn(c,r,v)
            if callable(fill):
                pbar = fill((bar_width, positive_height_fn(v)))
                nbar = fill((bar_width, negative_height_fn(v)))
            elif isinstance(fill, Image.Image):
                pbar = fill.resize((bar_width, positive_height_fn(v)))
                nbar = fill.resize((bar_width, negative_height_fn(v)))
            else:
                pbar = Image.new("RGBA", (bar_width, positive_height_fn(v)), fill)
                nbar = Image.new("RGBA", (bar_width, negative_height_fn(v)), fill)
            if type in [BarChartType.STACKED, BarChartType.STACKED_PERCENTAGE]:
                bar = pbar
                if clabels is not None:
                    label = clabel_fn(c,r,v,bar.width,bar.height)
                    if label is None:
                        continue
                    elif isinstance(label, ImageFont.FreeTypeFont):
                        label = Image.from_text(str(data.columns[c]), label, fg=fg, bg=bgtransparent)
                    bar = bar.place(label)
            else:
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
    if legend_labels is not None and legend_box is not None:
        labels = []
        for c in range(len(data.columns)):
            box = lbox_fn(c)
            if not isinstance(box, Image.Image):
                box = Image.new("RGBA", box, bg)
            fill = lcolor_fn(c)
            if callable(fill): fill = fill(box.size)
            elif isinstance(fill, Image.Image): fill = fill.resize(box.size)
            else: fill = Image.new("RGBA", box.size, fill)
            box.overlay(fill, mask=box)
            label = llabel_fn(c)
            if isinstance(label, ImageFont.FreeTypeFont):
                label = Image.from_text(str(data.columns[c]), label, fg=fg, bg=bg)
            labels.append([box, label])
        legend = Image.from_array(labels, padding=(2,5), xalign=[0.5, 0], bg=bg).pad(2,bg).pad(1, fg).pad(10)
        chart = chart.place(legend, lalign)

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
    if clabels is not None and type not in [BarChartType.STACKED, BarChartType.STACKED_PERCENTAGE]:
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
                elif clabels_pos == BarChartLabelPosition.BAR:
                    y = y_coordinate_fn(v) + int(v < 0)
                elif clabels_pos ==  BarChartLabelPosition.TOP:
                    y = y_coordinate_fn(ymax) + int(v <= 0)
                elif clabels_pos ==  BarChartLabelPosition.BOTTOM:
                    y = y_coordinate_fn(ymin) + int(v <= 0)
                label_at_top = y <= y_coordinate_fn(0)
                chart = chart.pin(label, (x, y), align=(0.5,int(label_at_top)), bg=bg, offsets=offsets)
    
    # Row labels
    if rlabels is not None:
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
            if rlabels_pos ==  BarChartLabelPosition.TOP:
                chart = chart.pin(label, (x, 0), align=(0.5,1), bg=bg, offsets=offsets)
            elif rlabels_pos ==  BarChartLabelPosition.BOTTOM:
                chart = chart.pin(label, (x, chart.height - offsets.y), align=(0.5,0), bg=bg, offsets=offsets)
            # TODO: support BAR in stacked mode
        
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

def time_chart(groups, start_key, end_key, color_key, chart_width, timeline_height,
               fg="white", bg="black", xmin=None, xmax=None, title=None,
               group_order=None, group_labels=None, group_info=None, element_images=None,
               grid_interval=None, label_interval=Ellipsis, grid_labels=None, label_format=str):
    """Plot a time chart. Times can be numeric, dates or anything that supports arithmetic.
    - groups (pandas groupby): group map containing time series
    - start_key (key or row->time): start time for a given record
    - end_key (key or row->time): end time for a given record
    - color_key (key or row->color): color for a given record
    - chart_width (int): chart width
    - timeline_height (int): height for each timeline
    - fg (color): text and grid color [white]
    - bg (color): background color [black]
    - xmin (time): chart start time [auto]
    - xmax (time): chart end time [auto]
    - title (image): image to use for title [none]
    - group_order (key sequence): optional group key ordering
    - group_labels (group->font/image): timeline labels on the left [none]
    - group_info (group->font/image): timeline info on the right [none]
    - element_images (record,width,height->image): element label, only used if it fits [none]
    - grid_interval (timedelta): grid line interval from start [start and end only]
    - label_interval (timedelta): grid label interval [grid_interval]
    - grid_labels (time->font/image): grid labels [none]
    - label_format (time->string): grid label format if using fonts [str]
    Functional arguments don't need to accept all the arguments and can also be passed in as
    constants.
    """

    start_fn = start_key if callable(start_key) else lambda d: get_non(d, start_key)
    end_fn = end_key if callable(end_key) else lambda d: get_non(d, end_key)
    color_fn = color_key if callable(color_key) else lambda d: get_non(d, color_key)
    group_label_fn = group_labels if callable(group_labels) else lambda g: group_labels
    group_info_fn = group_info if callable(group_info) else lambda g, r: group_info
    grid_label_fn = grid_labels if callable(grid_labels) else lambda v: grid_labels
    
    if xmin is None:
        xmin = min(start_fn(d) for _,df in groups for _,d in df.iterrows())
    if xmax is None:
        xmax = max(end_fn(d) for _,df in groups for _,d in df.iterrows())
    if xmin >= xmax:
        raise ValueError("Mininum x value {0:.3g} must be smaller than maximum x vaue {0:.3g}".format(xmin, xmax))
    def xvalue(x):
        return int((delimit(x,xmin,xmax) - xmin) / (xmax - xmin) * chart_width )
    if grid_interval is None:
        grid_interval = xmax-xmin
    if label_interval is Ellipsis:
        label_interval = grid_interval
    
    # chart
    timelines = []
    for g in group_order or groups.groups:
        r = groups.get_group(g)
        timeline = Image.new("RGBA", (chart_width, timeline_height), bg)
        for _,d in r.iterrows():
            start, end = xvalue(start_fn(d)), xvalue(end_fn(d))
            bar = Image.new("RGBA", (end-start, timeline_height), color_fn(d)).pad((1,0,0,0), bg)
            if element_images is not None:
                img = ignoring_extra_args(element_images)(d, bar.width, bar.height)
                if img.width < bar.width and img.height < bar.height:
                    bar = bar.place(img)
            timeline.overlay(bar, (start, 0))
        row, xalign = [timeline], [0.5]
        if group_labels is not None:
            label = group_label_fn(g)
            if isinstance(label, ImageFont.FreeTypeFont):
                label = Image.from_text(str(g), label, fg=fg, bg=bg)
            row, xalign = [label] + row, [1] + xalign
        if group_info is not None:
            info = group_info_fn(g,r)
            if not isinstance(info, Image.Image):
                info = Image.from_text(str(info), group_label_fn(g), fg=fg, bg=bg)
            row, xalign = row + [info], xalign + [0]
        timelines.append(row)
    chart = Image.from_array(timelines, padding=(4,5), bg=bg, xalign=xalign)
    
    # grid
    xoffset = 0 if group_labels is None else max(row[0].width for row in timelines)+4*3
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
    if label_interval is not None and grid_labels is not None:
        yoffset = chart.height
        grid_val = xmin
        while grid_val <= xmax:
            label = grid_label_fn(grid_val)
            if isinstance(label, ImageFont.FreeTypeFont):
                label = Image.from_text(label_format(grid_val), label, fg=fg, bg=bg, padding=(0,5,0,0))
            chart = chart.pin(label, (xoffset+xvalue(grid_val), yoffset), align=(0.5,0), bg=bg)
            grid_val += label_interval
    
    if title is not None: chart = Image.from_column((title, chart), bg=bg)
    return chart

# Image grids

def grid_chart(data, image_key, image_process=None,
               fg="white", bg="black", xalign=0.5, yalign=0.5, padding=(0,0,0,0),
               row_label=None, col_label=None, title=None):
    """Plot an image grid chart.
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
    
def name_csv_path(map): return splitext(map)[0] + ".csv"
def labelbox_img_path(map): return splitext(map)[0] + "_lbox" + splitext(map)[1]
def labelbox_csv_path(map): return splitext(map)[0] + "_lbox.csv"

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
    pd.DataFrame(rs).to_csv(name_csv_path(map), index=False)

def load_name_csv(map):
    return pd.read_csv(name_csv_path(map)).split_columns('color', '|', int)
    
def generate_labelbox_csv(map):
    """Generate a label bounding box csv, for use in map_chart."""
    img = Image.open(labelbox_img_path(map))
    logger.info("Generating labelbox CSV file at {}".format(labelbox_csv_path(map)))
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
    pd.DataFrame(rs).to_csv(labelbox_csv_path(map), index=False)

def load_labelbox_csv(map):
    return pd.read_csv(labelbox_csv_path(map)).split_columns(('bbox', 'color'), '|', int)
    
def generate_tile_map(array, filename, size, border=0, bg="white"):
    """Generate a map image and related files from an array of labels."""
    # TODO: border, namefile, lboxfile
    if isinstance(size, Integral): size = (size, size)
    labels = { l for row in array for l in row if not non(l) }
    colmap = lambda i: ((i%40)*5+(i//40), (i%40)*5+(i//40), 200-(i//100)*5)
    palette = { l : colmap(i) for i,l in enumerate(labels) }
    imgarray = [ [ None if non(l) else Image.new("RGB", size, palette[l]) for l in row ] for row in array ]
    img = Image.from_array(imgarray, bg=bg).convert("RGB")
    img.save(filename)
    names = [{ 'color': "|".join(str(x) for x in c), 'name': l } for l,c in palette.items()]
    pd.DataFrame(names).to_csv(name_csv_path(filename), index=False)
    img.save(labelbox_img_path(filename))
    generate_labelbox_csv(filename)
    
def map_chart(map, color_fn, label_fn=None, label_font=None, label_color="black"):
    """Generate a map chart from a map image and color mapping. If present, this will use a name csv file with image names
    and a label csv file with label bounding boxes.
    - map (filename): map image filename (and template for the name and label csv filenames).
    - color_fn (name -> color/pattern/None): a dict or function that gets passed each region name (or color tuple, if there isn't one) and returns a new color, pattern, or None (to leave the region unchanged).
    - label_fn (name, width, height -> text/image/None): an dict or function that returns either a text label or image. The label location is determined from the label csv file. [None]
    - label_font (font): font to use for text labels. [None]
    - label_color (color): color to use for text labels. [black]
    """
    
    # read image and name csv
    img = Image.open(map)
    try:
        df = load_name_csv(map)
        logger.info("Using color name file {}".format(name_csv_path(map)))
        namemap = { tuple(d['color']) : d['name'] for _,d in df.iterrows() }
    except FileNotFoundError:
        logger.warning("No color name file found at {}".format(name_csv_path(map)))
        namemap = {}
        
    # generate map
    colors = [(c,namemap.get(c, c)) for _,c in img.getcolors()]
    for c,name in colors:
        color = color_fn(name) if callable(color_fn) else color_fn.get(name)
        if color is None:
            continue
        elif isinstance(color, Image.Image):
            mask = img.select_color(c)
            pattern = Image.from_pattern(color, img.size)
            img.place(pattern, mask=mask, copy=False)
        else:
            img = img.replace_color(c, color)
            
    # generate labels
    if label_fn is not None:
        df = load_labelbox_csv(map)
        logger.info("Using label bounding box file {}".format(labelbox_csv_path(map)))
        labelboxes = { tuple(d["color"]) : BoundingBox(d['bbox']) for _,d in df.iterrows() }
        for c,name in colors:
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
                img = img.pin(label, labelboxes[c].center)
    return img
            
