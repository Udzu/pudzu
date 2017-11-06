import sys
sys.path.append('..')
from charts import *

CONFEDERATE = ["South Carolina", "Mississippi", "Florida", "Alabama", "Georgia", "Louisiana", "Texas"]
UNION = ["California", "Connecticut", "Illinois", "Indiana", "Iowa", "Kansas", "Maine", "Massachusetts", "Michigan", "Minnesota", "Nevada", "New Hampshire", "New Jersey", "New York", "Ohio", "Oregon", "Pennsylvania", "Rhode Island", "Vermont", "Dist. of Col.", "Wisconsin"]

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

def color_fn(c, r, v): return VEGA_PALETTE[int(v<0)]

def clabel_fn(c, r):
    # TODO: bold winner, italics loser?
    label = "[civil war]" if r == 1 else "{}\n{}\n{}".format(votes.index[r],votes.iloc[r]["rep_can"],votes.iloc[r]["dem_can"])
    return Image.from_text(label, arial(16), bg="white", align="center", padding=(0,2))
    
bar_chart(votes[["leaning"]], 80, 400, spacing=5, colors=color_fn, clabels=clabel_fn, clabels_pos=BarChartLabelPosition.BAR,
    ymin=-1, ymax=1, grid_interval=0.25, ylabels=arial(16)).show()
