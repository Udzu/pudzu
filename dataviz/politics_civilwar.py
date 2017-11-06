import sys
sys.path.append('..')
from charts import *
import seaborn as sns

CONFEDERATE = ["South Carolina", "Mississippi", "Florida", "Alabama", "Georgia", "Louisiana", "Texas"]
UNION = ["California", "Connecticut", "Illinois", "Indiana", "Iowa", "Kansas", "Maine", "Massachusetts", "Michigan", "Minnesota", "Nevada", "New Hampshire", "New Jersey", "New York", "Ohio", "Oregon", "Pennsylvania", "Rhode Island", "Vermont", "Dist. of Col.", "Wisconsin"]
PALETTE = ImageColor.from_floats(sns.color_palette())
DCOL = PALETTE[0]
RCOL = PALETTE[2]

try:
    votes = pd.read_csv("cache/politics_civilwar.csv").set_index("year")
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
    votes.to_csv("cache/politics_civilwar.csv")

def color_fn(c, r, v):
    return DCOL if v < 0 else RCOL

def ylabel_fn(v):
    if v == 0: return "same"
    party = "Rep" if v < 0 else "Dem"
    factor = "∞" if abs(v) == 1 else "{0:.2g}".format(1 / (1 - abs(v)))
    return "×{}{}".format(factor, party)
    
SIZE = 12

def clabel_fn(c, r):
    if r == 1: # 1864
        img = Image.from_column([
            Image.from_text("{}".format(votes.index[r]), arial(SIZE, bold=True), bg="white"),
            Image.from_text("Civil War", arial(SIZE, bold=True), "grey", bg="white")
            ], bg="white", padding=(0, 1))
    rep = votes.iloc[r]["rep_can"] in votes.iloc[r]["president"]
    img = Image.from_column([
        Image.from_text("{}".format(votes.index[r]), arial(SIZE, bold=True), bg="white"),
        Image.from_text(votes.iloc[r]["rep_can"], arial(SIZE, bold=rep), RCOL, bg="white"),
        Image.from_text(votes.iloc[r]["dem_can"], arial(SIZE, bold=not rep), DCOL, bg="white", padding=((int(votes.iloc[r]["dem_can"] == "Wilson"), 0)))
        ], bg="white", padding=(0, 1))
    return img.pad((0, 0, 0, 2), 0)
    
ylabel = Image.from_text("political leaning of the South versus the North", arial(24), padding=(0,2,0,10), bg="white").transpose(Image.ROTATE_90)

title = Image.from_column([
     Image.from_text("From Solid South to Republican heartland".upper(), arial(60), bg="white")
    , Image.from_text("the political transition of the U.S. South in presidential elections".upper(), arial(36), bg="white")
    ], bg="white", padding=(0, 3))

img = bar_chart(votes[["leaning"]], 62, 1000, spacing=2, colors=color_fn, clabels=clabel_fn, clabels_pos=BarChartLabelPosition.BAR,
    ymin=-1, ymax=1, grid_interval=0.125, ylabels=arial(SIZE), yformat=ylabel_fn, ylabel=ylabel, title=title)
    
# TODO: add labels
# - Catholic
# - Civil Rights Act
# - Southern strategy
    
img.save("output/politics_northsouth.png")
