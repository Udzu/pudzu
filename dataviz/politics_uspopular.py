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

def winner(y):
    return votes.rep_can[y] if  votes.rep_can[y] in votes.president[y] else votes.dem_can[y]
    
def loser(y):
    return votes.dem_can[y] if  votes.rep_can[y] in votes.president[y] else votes.rep_can[y]
    
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
    , Image.from_text("% margin since 1860 between the election winner and loser with most votes".upper(), arial(36), bg="white")
    ], bg="white", padding=(0, 5)).pad((0,0,0,10), "white")

img = bar_chart(votes[["margin"]], 62, 1000, spacing=2, colors=color_fn, clabels=clabel_fn, clabels_pos=BarChartLabelPosition.BAR,
    ymin=-0.0501, ymax=0.301, label_interval=0.05, grid_interval=0.025, ylabels=arial(FONT_SIZE), yformat="{:.0%}", ylabel=ylabel, title=title)

# Photos
PHOTOS = [
(1876, "https://upload.wikimedia.org/wikipedia/commons/6/60/SamuelJonesTilden.png", "https://upload.wikimedia.org/wikipedia/commons/e/ed/RutherfordBHayes.png", "3.02%"),
(2016, "https://upload.wikimedia.org/wikipedia/commons/2/28/Hillary_Clinton_by_Gage_Skidmore_2.jpg", "https://upload.wikimedia.org/wikipedia/commons/0/05/Official_Portrait_of_President_Donald_Trump_%28cropped%29.jpg", "2.10%"),
(1888, "https://upload.wikimedia.org/wikipedia/commons/f/f3/Grover_Cleveland_-_NARA_-_518139_%28cropped%29.jpg", "https://upload.wikimedia.org/wikipedia/commons/7/7e/Pach_Brothers_-_Benjamin_Harrison.jpg", "0.79%"),
(2000, "https://upload.wikimedia.org/wikipedia/commons/c/c5/Al_Gore%2C_Vice_President_of_the_United_States%2C_official_portrait_1994.jpg", "https://upload.wikimedia.org/wikipedia/commons/d/d4/George-W-Bush.jpeg", "0.51%"),
(1960, "https://upload.wikimedia.org/wikipedia/commons/0/09/VP-Nixon_copy_%283x4%29.jpg", "https://upload.wikimedia.org/wikipedia/commons/5/5e/John_F._Kennedy%2C_White_House_photo_portrait%2C_looking_up.jpg", "??")
]

LSIZE = 20

label = Image.from_text("Presidents\nwho lost the\npopular vote:".upper(), arial(LSIZE, bold=True), bg="white", padding=10, align="right")

photo_array = [
 [Image.from_row([
    Image.from_text("{}{}".format(y, "?"*int(y == 1960)), arial(LSIZE, bold=True), bg="white"),
    Image.from_text(" (see notes)" if y == 1960 else " (by {})".format(p), arial(LSIZE), bg="white")], bg="white"),
  Image.from_array([
    [Image.from_url_with_cache(w).crop_to_aspect(200, 300, (0.5, 0.2)).resize_fixed_aspect(width=100),
     Image.from_url_with_cache(l).crop_to_aspect(200, 300, (0.5, 0.2)).resize_fixed_aspect(width=100)],    
    [Image.from_text(winner(y), arial(LSIZE, bold=True), RCOL if votes.rep_can[y] in votes.president[y] else DCOL, bg="white"),
     Image.from_text(loser(y), arial(LSIZE, bold=False), DCOL if votes.rep_can[y] in votes.president[y] else RCOL, bg="white")]], bg="white", padding=(0,2))]
  for (y, l, w, p) in PHOTOS]
photos = Image.from_array(list(zip(*photo_array)), bg="white", padding=(10,2))

notes = Image.from_column([
Image.from_text("Notes", arial(LSIZE, bold=True), bg="white", padding=(0,2)),
Image.from_text("[1824] John Quincy Adams also lost the popular vote in 1824, though a third of states still didn't vote for their electors.\n[1860] Northern Democrat Douglas received the second most votes in 1860, though Southern Democrat Breckinridge and Consitutional Unionist John Bell both received more electoral votes.\n[1912] Roosevelt was runner-up in both votes and electoral votes in 1912 while running for the Progressive (\"Bull Moose\") Party\n[1960] The unusual nature of the 1960 election in Alabama, where voters voted for multiple electors rather than a slate, makes it possible to argue that Nixon actually won the popular vote.\n[2016] Trump falsely claimed that he \"won the popular vote if you deduct the millions of people who voted illegally\".", arial(LSIZE), bg="white", max_width=1200, padding=(0,2))],
bg="white", padding=(40,0,10,0), xalign=0)

footer = Image.from_row([label, photos, notes], bg="white").pad((0,0,0,10), "white")
img = Image.from_column([img, footer], bg="white")
    
# Save
img = img.pad((10,0), "white")
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/politics_uspopular.png")
