import sys
sys.path.append('..')
from charts import *
import seaborn as sns
from dates import *
import dateparser

CONFEDERATE = ["South Carolina", "Mississippi", "Florida", "Alabama", "Georgia", "Louisiana", "Texas"] + ["Arkansas", "North Carolina", "Tennessee", "Virginia"]
UNION = ["California", "Connecticut", "Illinois", "Indiana", "Iowa", "Kansas", "Maine", "Massachusetts", "Michigan", "Minnesota", "Nevada", "New Hampshire", "New Jersey", "New York", "Ohio", "Oregon", "Pennsylvania", "Rhode Island", "Vermont", "Dist. of Col.", "Wisconsin"]
BORDER = ["Delaware", "Kentucky", "Maryland", "Missouri", "West Virginia"]

PALETTE = ImageColor.from_floats(sns.color_palette())
DCOL = PALETTE[0]
RCOL = PALETTE[2]
EVENTBG = "#555555"
FONT_SIZE = 12

EVENTS = [
("Civil War", "April 12, 1861", "May 9, 1865"),
("Reconstruction", "May 10, 1865", "March 31, 1877"),
("Redemption", "April 1, 1877", "January 1, 1910"),
("Jim Crow", "January 2, 1910", "July 25, 1948"), 
("Civil Rights", "July 26, 1948", "December 31, 1967"), 
("“Southern Strategy”", "January 1, 1968", "November 7, 2017") 
]

# Generate data
try:
    votes = pd.read_csv("cache/politics_usnorthsouth.csv").set_index("year")
except OSError:
    votes = pd.read_csv("datasets/uselections_ucsb.csv", dtype={"rep_col": str, "dem_col": str}).split_columns(("rep_col", "dem_col"), "|").set_index("year")

    def get_votes(df, state, year, republican):
        cols = list(map(int,make_sequence(votes["rep_col" if republican else "dem_col"][year])))
        if state not in df.index: state = state + "*"
        if state not in df.index: return 0
        return df.loc[state][cols].apply(ignoring_exceptions(int, 0)).sum()

    records = []
    for y in range(1860,2017,4):
        if y == 1864: 
            votes.set_value(y, "leaning", 0)
        else:
            tclass = "elections_states" if y != 1976 else "ver11"
            dfs = pd.read_html("http://www.presidency.ucsb.edu/showelection.php?year={}".format(y), "Alabama", attrs={"class": tclass})
            df = dfs[0].set_index(0)
            union_rep = sum(get_votes(df, s, y, True) for s in UNION)
            union_dem = sum(get_votes(df, s, y, False) for s in UNION)
            conf_rep = sum(get_votes(df, s, y, True) for s in CONFEDERATE)
            conf_dem = sum(get_votes(df, s, y, False) for s in CONFEDERATE)
            ratio = (union_rep/union_dem)/(conf_rep/conf_dem)
            leaning = (ratio - 1) if ratio < 1 else 1 - (1 / ratio)
            votes.set_value(y, "leaning", leaning)
            print("{},{},{},{},{},{}".format(y, union_rep, union_dem,conf_rep, conf_dem, leaning))
    votes.to_csv("cache/politics_usnorthsouth.csv")

# Bar chart
def color_fn(c, r, v):
    return RCOL if v < 0 else DCOL

def ylabel_fn(v):
    if v == 0: return "same"
    party = "Rep" if v < 0 else "Dem"
    factor = "∞" if abs(v) == 1 else "{0:.2g}".format(1 / (1 - abs(v)))
    return "×{} {}".format(factor, party)
    
def clabel_fn(c, r):
    if votes.index[r] == 1864:
        img = Image.from_column([
            Image.from_text("{}".format(votes.index[r]), arial(FONT_SIZE, bold=True), bg="white", padding=(1,1)),
            Image.from_text("Civil War", arial(FONT_SIZE, bold=True), "grey", bg="white", padding=(1,1))
            ], bg=0)
    else:
        v = votes.iloc[r]
        rep = v["rep_can"] in v["president"]
        img = Image.from_column([
            Image.from_text("{}".format(votes.index[r]), arial(FONT_SIZE, bold=True), bg="white", padding=(1,1)),
            Image.from_text(votes.iloc[r]["rep_can"], arial(FONT_SIZE, bold=rep), RCOL, bg="white", padding=((int(len(v["rep_can"]) < 8), 1))),
            Image.from_text(votes.iloc[r]["dem_can"], arial(FONT_SIZE, bold=not rep), DCOL, bg="white", padding=((int(len(v["dem_can"]) < 8), 1)))
            ], bg=0)
    return img.pad((0, 0, 0, 2), 0)
    

ylabel = Image.from_column([
Image.from_text("political leaning of the South versus the North", arial(24), padding=(5,2,5,5), bg="white"),
Image.from_text("based on the ratio of Republican to Democrat votes in the South divided by the ratio in the North", arial(14), padding=(5,2,5,10), bg="white")], bg="white").transpose(Image.ROTATE_90)

title = Image.from_column([
     Image.from_text("From ‘Solid South’ to Republican heartland".upper(), arial(60, bold=True), bg="white")
    , Image.from_text("the political transformation of the U.S. South in presidential elections".upper(), arial(36), bg="white")
    ], bg="white", padding=(0, 5)).pad((0,0,0,10), "white")

img = bar_chart(votes[["leaning"]], 62, 1000, spacing=2, colors=color_fn, clabels={ BarChartLabelPosition.OUTSIDE : clabel_fn},
    ymin=-1, ymax=1, grid_interval=0.125, ylabels=arial(FONT_SIZE), yformat=ylabel_fn, ylabel=ylabel, title=title)
    
# Add time chart
events = pd.DataFrame([{ "group": "event", "name": n, "start": dateparser.parse(s).date(), "end": dateparser.parse(e).date() } for n,s,e in EVENTS])
groups = events.groupby("group")
chronology = time_chart(groups, "start", "end", lambda _: EVENTBG, 2620, 50, element_images=lambda d: Image.from_text(d['name'], arial(16), fg="white", bg=EVENTBG), bg="white")
img = img.place(chronology, (0, 1), padding=(150,100))

# Add state map
UNION = ["District of Columbia" if x == "Dist. of Col." else x for x in UNION]
def state_color_fn(c):
    if c == "Borders": return "white"
    elif c in UNION: return DCOL
    elif c in CONFEDERATE: return RCOL
    elif c in BORDER: return "grey"
    else: return "#BBBBBB"
map = map_chart("maps/USA.png", state_color_fn)
map_thumb = Image.from_column([
    Image.from_text("‘South’ refers to ex-Confederate states\n‘North’ refers to ex-Union non-border states", arial(60, bold=True), line_spacing=5),
    map
], bg="white").resize_fixed_aspect(width=500)
img = img.place(map_thumb, (1, 0), padding=(80, 200))

# Save
img = img.pad((10,0), "white")
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/politics_usnorthsouth.png")
