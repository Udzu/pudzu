import sys
sys.path.append('..')
from charts import *
import seaborn as sns

PALETTE = ImageColor.from_floats(sns.color_palette())
DCOL = PALETTE[0]
RCOL = PALETTE[2]
FONT_SIZE = 12

# Generate data
try:
    votes = pd.read_csv("cache/politics_uspopular.csv").set_index("year")
except OSError:
    votes = pd.read_csv("datasets/uselections_ucsb.csv", dtype={"rep_col": str, "dem_col": str}).split_columns(("rep_col", "dem_col"), "|", int).set_index("year")

    def get_margin(df, year):
        
        cols = list(map(int,make_sequence(votes["rep_col" if republican else "dem_col"][year])))
        if state not in df.index: state = state + "*"
        if state not in df.index: return 0
        return df.loc[state][cols].apply(ignoring_exceptions(int, 0)).sum()

    records = []
    for y in range(1860,2017,4):
        tclass = "elections_states" if y != 1976 else "ver11"
        dfs = pd.read_html("http://www.presidency.ucsb.edu/showelection.php?year={}".format(y), "Rhode Island", attrs={"class": tclass})
        df = dfs[0].set_index(0)
        trow = "Totals" if "Totals" in df.index else "Total"
        total_votes = int(df[1][trow])
        win_col = (votes.rep_col[y] if votes.rep_can[y] in votes.president[y] else votes.dem_col[y])[0]
        win_votes = int(df[win_col][trow])
        sec_col = 2 if win_col == 5 else 5
        sec_votes = int(df[sec_col][trow])
        margin = (win_votes - sec_votes) / total_votes
        votes.set_value(y, "margin", margin)
        print(y, votes.president[y], total_votes, win_votes, sec_votes, margin)
    votes.to_csv("cache/politics_uspopular.csv")

# Bar chart

def color_fn(c, r, v):
    y = votes.index[r]
    return RCOL if votes.rep_can[y] in votes.president[y] else DCOL

def clabel_fn(c, r):
    y = votes.index[r]
    rep = votes.rep_can[y] in votes.president[y]
    win_can = votes.rep_can[y] if rep else votes.dem_can[y]
    if y in [1960, 2016]: win_can = win_can + "*"
    los_can = "Roosevelt*" if y == 1912 else "Douglas*" if y == 1860 else votes.dem_can[y] if rep else votes.rep_can[y]
    win_col = RCOL if rep else DCOL
    los_col = PALETTE[1] if y == 1912 else DCOL if rep else RCOL
    img = Image.from_column([
        Image.from_text("{}".format(votes.index[r]), arial(FONT_SIZE, bold=True), bg="white", padding=(1,1)),
        Image.from_text(win_can, arial(FONT_SIZE, bold=True), win_col, bg="white", padding=((int(len(win_can) < 8), 1))),
        Image.from_text(los_can, arial(FONT_SIZE, bold=False), los_col, bg="white", padding=((int(len(los_can) < 8), 1)))
        ], bg=0)
    return img.pad((0, 0, 0, 2), 0)
    
ylabel = Image.from_text("popualr vote margin by percentage", arial(24), padding=(5,2,5,10), bg="white").transpose(Image.ROTATE_90)

title = Image.from_column([
     Image.from_text("popular vote margin in U.S. presidential elections".upper(), arial(60, bold=True), bg="white")
    , Image.from_text("margin by percentage between the election winner and loser with most votes".upper(), arial(36), bg="white")
    ], bg="white", padding=(0, 5)).pad((0,0,0,10), "white")

img = bar_chart(votes[["margin"]], 62, 1000, spacing=2, colors=color_fn, clabels=clabel_fn, clabels_pos=BarChartLabelPosition.BAR,
    ymin=-0.0501, ymax=0.301, label_interval=0.05, grid_interval=0.025, ylabels=arial(FONT_SIZE), yformat="{:.0%}", ylabel=ylabel, title=title)
    
footer = Image.from_text("[1860] Northern Democrat Douglas received the second most votes in 1860, though Southern Democrat Breckinridge and Consitutional Unionist John Bell both received more electoral votes.\n[1912] Roosevelt was runner-up in both votes and electoral votes in 1912 while running for the Progressive (\"Bull Moose\") Party\n[1960] The unusual nature of the 1960 election in Alabama makes it possible to argue that Nixon actually won the popular vote.\n[2016] Trump falsely claimed that he \"won the popular vote if you deduct the millions of people who voted illegally\".", arial(16), padding = 10)
img = Image.from_column([img, footer], bg="white")
    
# Save
img = img.pad((10,0), "white")
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/politics_uspopular.png")
