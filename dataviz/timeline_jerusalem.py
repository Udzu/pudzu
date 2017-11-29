import sys
sys.path.append('..')
from charts import *
from dates import *

# -------------
# G7 time chart
# -------------

df = pd.read_csv("datasets/timeline_jerusalem.csv").split_columns("type", "|")

START, END = -2000, 2000
INTERVAL = 500
COLORS = { "christian": "#e41a1c", "pagan": "#ff7f00", "jewish": "#377eb8", "muslim": "#4daf4a" }

def stripes(colors): return Image.from_column([Image.new("RGBA", (100, 4), c) for c in colors])

labelfn = lambda d, w: " " if ("Herod" in d['period'] or "Mamluk" in d['period']) and w < 50 else d['period']
colorfn = lambda d, w, h: Image.from_pattern(stripes([COLORS[t] for t in d['type']]), (w, h))

labeld = {frozenset({TimeChartLabelPosition.ABOVE, TimeChartLabelPosition.INSIDE, TimeChartLabelPosition.BELOW}): labelfn,
          TimeChartLabelPosition.ABOVE: " ", TimeChartLabelPosition.BELOW: " "}
data = [df.filter_rows("start<{} and end>{}".format(start+INTERVAL, start)).update_columns(start=lambda v: v-start, end=lambda v: v-start) for start in range(START, END, INTERVAL)]
llabels = ["{} BC".format(-start) if start< 0 else "AD {}".format(start+int(start==0)) for start in range(START, END, INTERVAL)]

chart = time_chart(data, 800, 40, "start", "end", colorfn, labels=labeld, label_font=arial(10), 
                   xmin=0, xmax=INTERVAL, grid_font=arial(10), grid_labels=lambda v: "+{}".format(v), grid_interval=100, labels_left=llabels).pad(2, bg="black")

chart.save("output/timeline_jerusalem.png")

# def duration(d):
    # return END - max(START, dateparser.parse(d['start']).date())
    
# def percentage_left(df):
    # return sum((duration(d) for _,d in df[df.spectrum == "left"].iterrows()), datetime.timedelta(0)) / sum((duration(d) for _,d in df.iterrows()), datetime.timedelta(0))
    
# groups = pd.read_csv("datasets/g7.csv").groupby_rows(lambda d: "{} ({})".format(d['country'], d['office']))
# group_order = sorted(list(groups.groups), key=lambda s: percentage_left(groups.get_group(s)), reverse=True)

# colorfn = lambda d: {"left": "#d62728", "right": "#393b79", "centre": "#e7ba52"}[d['spectrum']]
# chart = time_chart(groups, lambda d: dateparser.parse(d['start']).date(), lambda d: dateparser.parse(get_non(d, 'end', END.isoformat())).date(), colorfn, 1200, 40, xmin=START, group_labels=arial(16), group_order=group_order, group_info=lambda g,r: "{:.0%}".format(percentage_left(r)), title=Image.from_text("G7 countries by time spent under left-of-centre governments (1960-present)", arial(30, bold=True), fg="white").pad((0,5,0,30),bg="black"), grid_interval=DateInterval(years=10), element_images=lambda d: Image.from_text(d['name'].split(" ")[-1], arial(10), padding=(5,2), fg="white", bg=colorfn(d)), grid_labels=arial(16), label_format=lambda v: str(v.year)).pad(5, "black")
