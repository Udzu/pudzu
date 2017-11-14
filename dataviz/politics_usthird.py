import sys
sys.path.append('..')
from charts import *
import seaborn as sns

PALETTE = ImageColor.from_floats(sns.color_palette())
HLS = ImageColor.from_floats(sns.color_palette("hls", 16))

FONT_SIZE = 12

BLUE = PALETTE[0]
RED = PALETTE[2]
GREEN = PALETTE[1]
PINK = HLS[-2]
GREY = "grey"
ORANGE = '#db9000'

LEGEND = [
("Constitutional Union Party", "1860", "Big tent party whose main aim was to preserve the Union. There were two Democratic candidates this year (Northern and Southern).", ORANGE),
("none", "1864, 68", "No known third party candidates for 1864 and 1868, though deceased Republican elector Ellsworth Cheeseborough is recorded as getting 543 votes in 1864.", GREY),
("Straight-Out Democrats", "1872", "Conservative Southern Democrat faction who rejected Horace Greeley (the Liberal Republican who ran with Demoratic support).", BLUE),
("Greenback Party", "1880, 84", "Anti-monopolist labor party", GREEN),
("Prohibition Party", "1884, 88, 1900", "Temperance movement", PINK),
("People's Party", "1892", "Populist agrarian party and successor of the Greenback Party", GREEN),
("National Democratic Party", "1896", "Conservative Southern Democrat faction who rejected William Jennings Bryan (the Democratic and People's Party nominee).", BLUE),
# TODO
("Progressive Party", "1912", "Roosevelt's Progressive Party", GREEN),
("Socialist Party", "1904, 08, 16, 20, 28, 32, 40", "Democratic socialist party", RED),
("Progressive Party", "1924", "A diffeerent Progressive Party", GREEN),
("Union Party", "1936", "Some", "#7F3300"),
("Texas Regulars", "1944", "Democrats", BLUE),
("States' Rights Democratic", "1948", "Dixiecrats", ORANGE),
("Progressive Party", "1952", "A diffeerent Progressive Party", GREEN),
("States' Rights Party", "1956", "Also unpledged electors", GREY),
("Socialist Labor Party", "1960, 64", "Also unpledged electors", RED),
("American Independent Party", "1968", "Far-right", ORANGE),
("Eugene McCarthy", "1972", "Independent", GREY),
("John B. Anderson", "1976", "Independent", GREY),
("Libertarian Party", "1984, 88, 2012, 16", "Libertarian", GREY), # YELLOW
("Perot/Reform Party", "1992, 96", "Perot", GREY),
("Nader/Green Party", "2000, 04, 08", "Nader", GREEN)
]

# 1896:Bryan was People's as well as Democrat; breakaway
# 1944:no candidate fielded; top person was Thomas
# 1948:Truman also Liberal in NY
# 1956:unpledged electors got more
# 1960:unpledged electors voted for Byrd
# 1964:unpledged electors

PARTY_COL = { p : c for p, _, _, c in LEGEND }

# Generate data
votes = pd.read_csv("datasets/uselections_third.csv").set_index("year").update_columns(percent=lambda p: p / 100)

# Bar chart

def color_fn(c, r, v):
    return PARTY_COL.get(votes.party.iloc[r], PALETTE[0])

def clabel_fn(c, r):
    img = Image.from_column([
        Image.from_text("{}".format(votes.index[r]), arial(FONT_SIZE, bold=True), bg="white", padding=(1,1)),
        Image.from_text(get_non(votes.candidate,votes.index[r],"(none)").split(" ")[-1], arial(FONT_SIZE, bold=True), bg="white", padding=(1,1))
        ], bg=0)
    return img.pad((0, 0, 0, 2), 0)
    
def rlabel_fn(r):
    ev = votes.electoral.iloc[r]
    return None if ev == 0 else Image.from_text("{} EVs".format(ev), arial(FONT_SIZE, bold=True), bg="white", padding=(1,3))
    
ylabel = Image.from_text("popular vote percentage", arial(24), padding=(5,2,5,10), bg="white").transpose(Image.ROTATE_90)

title = Image.from_column([
     Image.from_text("top third party candidates in U.S. presidential elections".upper(), arial(60, bold=True), bg="white")
    , Image.from_text("non-Democrat/Republican candidate with highest popular vote since 1860".upper(), arial(36), bg="white")
    ], bg="white", padding=(0, 5)).pad((0,0,0,10), "white")

img = bar_chart(votes[["percent"]], 62, 1000, spacing=2, colors=color_fn, clabels=clabel_fn, clabels_pos=BarChartLabelPosition.BAR, rlabels=rlabel_fn,
    ymin=0, ymax=0.301, label_interval=0.05, grid_interval=0.025, ylabels=arial(FONT_SIZE), yformat="{:.0%}", ylabel=ylabel, title=title)
    
# Legend

legend = Image.from_array([[
Image.new("RGBA", (60,60), c).pad((10,0), "white"),
Image.from_column([
Image.from_text("{} [{}]".format(p, y), arial(16, bold=True), "black", "white"),
Image.from_text(d, arial(12), "black", "white", max_width=400)
], xalign=0)]
for p,y,d,c in LEGEND
], bg="white", xalign=0)

legend = legend.pad(10, "white").pad(1, "black").pad(5, "white")

img = img.pin(legend, (img.width, 0), align=0, bg="white")
    
# # Save
img = img.pad(10, "white")
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/politics_usthird.png")