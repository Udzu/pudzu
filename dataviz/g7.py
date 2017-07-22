import sys
sys.path.append('..')
from charts import *
from records import *
from dates import *
import dateparser

# -------------
# G7 time chart
# -------------

START = dateparser.parse('1 January 1960').date()
END = datetime.date.today()

def duration(d):
    return END - max(START, dateparser.parse(d['start']).date())
    
def percentage_left(rs):
    return sum((duration(d) for d in filter_records(rs, "spectrum=left")), datetime.timedelta(0)) / sum((duration(d) for d in rs), datetime.timedelta(0))
    
records = RecordCSV.load_file("g7.csv")
groups = sorted_groups(group_records(records, lambda d: "{} ({})".format(d['country'], d['office'])), lambda g,r: percentage_left(r), group_reverse=True)
colorfn = lambda d: {"left": "#d62728", "right": "#393b79", "centre": "#e7ba52"}[d['spectrum']]
chart = time_chart(groups, lambda d: dateparser.parse(d['start']).date(), lambda d: dateparser.parse(d.get('end', END.isoformat())).date(), colorfn, 1200, 40, xmin=START, group_labels=arial(16), group_info=lambda g,r: "{:.0%}".format(percentage_left(r)), title=Image.from_text("G7 countries by time spent under left-of-centre governments (1960-present)", arial(30, bold=True)).pad((0,5,0,30),bg="black"), grid_interval=DateInterval(years=10), element_images=lambda d: Image.from_text(d['name'].split(" ")[-1], arial(10), padding=(5,2), bg=colorfn(d)), grid_labels=arial(16), label_format=lambda v: str(v.year)).pad(5, "black")

def box(s): return Image.new("RGBA", (20,20), colorfn({"spectrum": s}))
def label(s): return Image.from_text(s, arial(12))

footer_row = [box("left"), label("left-of-centre"), box("centre"), label("centrist"), box("right"), label("right-of-centre"),
              Image.new("RGBA", (50,0)),
              Image.from_text("Colours are standard UK colours for conservatism, liberalism and social democracy.", arial(16)),
              Image.from_text("Note that they differ from the ones used in the US since 2000.", arial(16, bold=True))]
footer = Image.from_row(footer_row, padding=3, bg="black")
img = Image.from_column([chart, footer], bg="black", padding=(0,20))
img.save("g7.png")
