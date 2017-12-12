import sys
sys.path.append('..')
from charts import *

FONT_SIZE = 16

BLUE = "#377eb8"
RED = "#e41a1c"
GREEN = "#4daf4a"
PINK = "#f781bf"
GREY = "#999999"
ORANGE = "#ff7f00"
BROWN = "#7F3300"
YELLOW = "#ECC850"
PURPLE = "#984ea3"

LEGEND = [
("Constitutional Union Party", "1860", "Big tent party whose main aim was to preserve the Union. There were also two Democratic candidates this year (Northern and Southern).", ORANGE),
("none", "1864, 68", "No third party candidates for 1864/1868, though deceased Republican elector Ellsworth Cheeseborough is recorded as getting 543 votes in 1864.", GREY),
("Straight-Out Democrats", "1872", "Conservative Southern Democrat faction who rejected Horace Greeley (the Liberal Republican who ran with Demoratic support).", BLUE),
("Greenback Party", "1880, 84", "Anti-monopolist labor party.", GREEN),
("Prohibition Party", "1884, 88, 1900", "Temperance movement party.", PINK),
("People's Party", "1892", "Populist agrarian party and successor of the Greenback Party.", GREEN),
("National Democratic Party", "1896", "Conservative Southern Democrat faction who rejected William Jennings Bryan (the Democratic and People's Party nominee).", BLUE),
("Progressive Party", "1912", "Roosevelt's progressive \"Bull Moose Party\", founded after Roosevelt failed to capture the Republican nomination. Came second in the elections.", GREEN),
("Socialist Party", "1904, 08, 16, 20, 28, 32, 40", "A multi-tendency democratic-socialist and social-democratic party.", RED),
("Progressive Party", "1924", "Populist agragrian party unconnected to the Bull Moose Party.", GREEN),
("Union Party", "1936", "Populist isolationist party opposed to FDR's New Deal.", BROWN),
("Texas Regulars", "1944", "Conservative Texan Democrat faction opposed to FDR's New Deal. Didn't field a candidate.", BLUE),
("States' Rights Democratic", "1948", "Segregationist \"Dixiecrat\" party opposed to racial integration.", ORANGE),
("Progressive Party", "1952", "Left-wing party in favour of welfare state reforms and unconnected to the two prevsious Progressive Parties.", GREEN),
("States' Rights Party", "1956", "Populist right-wing party. Beaten by the 0.3% of the vote which went to unpledged Southern electors.", GREY),
("Socialist Labor Party", "1960, 64", "De Leonist socialist party. Beaten by the 0.4%/0.3% of the vote which went to unpledged Southern electors.", RED),
("American Independent Party", "1968, 72", "Right-wing segregationist party.", PURPLE),
("Eugene McCarthy", "1976", "Independent campaign by McCarthy, who'd previously sought the Democratic nomination, focused on ballot access.", GREY),
("John B. Anderson", "1980", "Independent campaign by Anderson, who'd sought the Republican nomination, running as a moderate counterpoint to Reagan.", GREY),
("Libertarian Party", "1984, 88, 2012, 16", "Libertarian party.", YELLOW),
("Perot/Reform Party", "1992, 96", "Protectionist, fiscally conservative campaigns by billionaire Ross Perot.", PURPLE),
("Nader/Green Party", "2000, 04, 08", "Campaigns focused on progressive consumer rights and government reform.", GREEN)
]

PARTY_COL = { p : c for p, _, _, c in LEGEND }

# Generate data
votes = pd.read_csv("datasets/uselections_third.csv").set_index("year").update_columns(percent=lambda p: p / 100)

# Bar chart

def color_fn(c, r, v):
    return PARTY_COL.get(votes.party.iloc[r], GREY)

def name_label_fn(c, r):
    img = Image.from_row([
        Image.from_text("{}: ".format(votes.index[r]), arial(FONT_SIZE, bold=True), bg="white", padding=(1,1)),
        Image.from_text(get_non(votes.candidate,votes.index[r],"(none)"), arial(FONT_SIZE, bold=False), bg="white", padding=(1,1,3,1))
        ], bg=0)
    return img.pad((0, 0, 0, 2), 0)
    
def ep_label_fn(c, r):
    ev = votes.electoral.iloc[r]
    pc = votes.percent.iloc[r]
    if ev > 0: return Image.from_text("{} Electoral Votes".format(ev), arial(FONT_SIZE, bold=True), bg="white", padding=(3,1))
    elif pc > 0.05: return Image.from_text("(no Electoral Votes!)", arial(FONT_SIZE, bold=True), bg="white", padding=(3,1))
    elif 0 < pc < 0.01: return Image.from_text("{:.1%}".format(pc), arial(FONT_SIZE, bold=True), bg="white", padding=(3,1))
    else: return None
    
def pc_label_fn(c, r):
    pc = votes.percent.iloc[r]
    return None if pc < 0.01 else Image.from_text("{:.1%}".format(pc), arial(FONT_SIZE, bold=True), fg="white", padding=1)
    
ylabel = Image.from_text("popular vote percentage", arial(24), padding=(5,2,5,10), bg="white")

title = Image.from_column([
     Image.from_text("top third party candidates in U.S. presidential elections".upper(), arial(60, bold=True), bg="white", padding=3)
    , Image.from_text("non-Democrat/Republican candidates with highest popular vote since 1860".upper(), arial(36), bg="white", padding=2)
    ], bg="white").pad((0,0,0,10), "white")

img = bar_chart(votes[["percent"]], 30, 1500, spacing=1, colors=color_fn, clabels={BarChartLabelPosition.OUTSIDE: ep_label_fn, BarChartLabelPosition.INSIDE: pc_label_fn, BarChartLabelPosition.AXIS: name_label_fn},
    ymin=0, ymax=0.301, label_interval=0.05, grid_interval=0.01, ylabels=arial(FONT_SIZE), yformat="{:.0%}", ylabel=ylabel, horizontal=True)
    
# Legend

legend = generate_legend([c for _,_,_,c in LEGEND], [Image.from_column([
Image.from_text("{} [{}]".format(p, y), arial(16, bold=True), "black", "white"),
Image.from_text(d, arial(12), "black", "white", max_width=400, padding=(0,2))
], xalign=0) for p,y,d,_ in LEGEND], box_sizes=(55,55), header="By political party".upper(), spacing=0, fonts=papply(arial, 20))

img = Image.from_row([img, legend], bg="white", padding=10)
img = Image.from_column([title, img], bg="white", padding=(0,10))
    
# # Save
img = img.pad(10, "white")
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/politics_usthird.png")
