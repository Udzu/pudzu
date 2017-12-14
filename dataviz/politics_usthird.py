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
("Constitutional Union Party", "1860", "Big tent party whose main aim was to preserve the Union. There were also two Democratic candidates this year (Northern and Southern).", ORANGE, "https://upload.wikimedia.org/wikipedia/commons/8/8c/John-bell-brady-handy-cropped.jpg"),
("none", "1864, 68", "No third party candidates for 1864/1868, though deceased Republican elector Ellsworth Cheeseborough received 543 votes in 1864.", GREY, "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2a/Flag_of_None.svg/1024px-Flag_of_None.svg.png"),
("Straight-Out Democrats", "1872", "Conservative Southern Democrat faction who rejected Horace Greeley (the Liberal Republican who ran with Demoratic support). Their candidate, O'Conor, declined their nomination.", BLUE, "https://upload.wikimedia.org/wikipedia/commons/9/90/Charles_OConor_-_Brady-Handy.jpg"),
("Greenback Party", "1880, 84", "Anti-monopolist labor party.", GREEN, "https://upload.wikimedia.org/wikipedia/commons/c/c6/James_Weaver_-_Brady-Handy.jpg"),
("Prohibition Party", "1884, 88, 1900", "Temperance movement party.", PINK, "https://upload.wikimedia.org/wikipedia/commons/e/eb/CBFisk.jpg"),
("People's Party", "1892", "Populist agrarian party and successor of the Greenback Party.", GREEN, "https://upload.wikimedia.org/wikipedia/en/6/6b/Weaver-James-1870s.jpg"),
("National Democratic Party", "1896", "Conservative Southern Democrat faction who rejected William Jennings Bryan (the Democratic and People's Party nominee).", BLUE, "https://upload.wikimedia.org/wikipedia/commons/f/f9/JohnMPalmer_small.png"),
("Progressive Party", "1912", "Roosevelt's \"Bull Moose Party\", founded after Roosevelt failed to capture the Republican nomination. Came second in the elections.", GREEN, "https://upload.wikimedia.org/wikipedia/commons/9/95/Theodore_Roosevelt-Pach.jpg"),
("Socialist Party", "1904, 08, 16, 20, 28, 32, 40", "A multi-tendency democratic-socialist and social-democratic party.", RED, "https://upload.wikimedia.org/wikipedia/commons/4/4b/Eugene_V_Debs_1912.jpg"),
("Progressive Party", "1924", "Populist agragrian party unconnected to the Bull Moose Party.", GREEN, "https://upload.wikimedia.org/wikipedia/commons/2/20/Robert_M_La_Follette%2C_Sr.jpg"),
("Union Party", "1936", "Populist isolationist party opposed to FDR's New Deal.", BROWN, "http://usamericanaauctions.com/ItemImages/000001/1320_lg.jpeg"),
("Texas Regulars", "1944", "Conservative Texan Democrat faction opposed to FDR's New Deal. Didn't field a candidate.", BLUE, "https://img.newspapers.com/img/thumbnail/44949096/400/400/0_0_4987_6825.jpg"),
("States' Rights Democratic", "1948", "Segregationist \"Dixiecrat\" party opposed to racial integration.", ORANGE, "https://upload.wikimedia.org/wikipedia/commons/1/10/StromThurmond.png"),
("Progressive Party", "1952", "Left-wing party in favour of welfare state reforms and unconnected to the two previous Progressive Parties.", GREEN, "http://guardiansofthecity.org/sheriff/images/inmates/vincent_hallinan.jpg"),
("States' Rights Party", "1956", "Populist right-wing party. Beaten by the 0.3% of the vote which went to unpledged Southern electors.", GREY, "http://www.azquotes.com/public/pictures/authors/8c/9f/8c9fb968141f6140b28b203eefc6dbac/547c40dd474f1_t_coleman_andrews.jpg"),
("Socialist Labor Party", "1960, 64", "Syndicalist Marxist party. Beaten by the ~0.3% of the vote which went to unpledged Southern electors.", RED, "https://pastdaily.com/wp-content/uploads/2017/11/Eric-Hass-1-resize.jpg"),
("American Independent Party", "1968, 72", "Right-wing segregationist party.", PURPLE, "https://upload.wikimedia.org/wikipedia/commons/c/c9/George_C_Wallace.jpg"),
("Eugene McCarthy", "1976", "Independent campaign by McCarthy, who'd previously sought the Democratic nomination, largely focused on ballot access.", GREY, "http://www.historycentral.com/Bio/people/images/mccarthy.gif"),
("John B. Anderson", "1980", "Independent campaign by Anderson, who'd sought the Republican nomination, running as a moderate counterpoint to Reagan.", GREY, "https://upload.wikimedia.org/wikipedia/commons/c/ca/JohnAnderson.png"),
("Libertarian Party", "1984, 88, 2012, 16", "Libertarian party.", YELLOW, "https://www.nationalreview.com/sites/default/files/gary-johnson-profile.jpg"),
("Perot/Reform Party", "1992, 96", "Protectionist, fiscally conservative campaigns by billionaire Ross Perot.", PURPLE, "https://i.ytimg.com/vi/Tz651SPuyck/hqdefault.jpg"),
("Nader/Green Party", "2000, 04, 08", "Campaigns focused on progressive consumer rights and government reform.", GREEN, "http://www.trbimg.com/img-57490004/turbine/la-le-al-gore-ralph-nader-2000-20160527-snap")
]

PARTY_COL = { p : c for p, _, _, c, *i in LEGEND }

# Bar chart
votes = pd.read_csv("datasets/uselections_third.csv").set_index("year").update_columns(percent=lambda p: p / 100)

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
    elif pc > 0.05: return Image.from_text("(no Electoral Votes)", arial(FONT_SIZE, bold=True), bg="white", padding=(3,1))
    elif 0 < pc < 0.01: return Image.from_text("{:.1%}".format(pc), arial(FONT_SIZE, bold=True), bg="white", padding=(3,1))
    else: return None
    
def pc_label_fn(c, r):
    pc = votes.percent.iloc[r]
    return None if pc < 0.01 else Image.from_text("{:.1%}".format(pc), arial(FONT_SIZE, bold=True), fg="white", padding=1)
    
ylabel = Image.from_text("popular vote share", arial(24), padding=(5,2,5,10), bg="white")

title = Image.from_column([
     Image.from_text("top third party candidates in U.S. presidential elections".upper(), arial(48, bold=True), bg="white", padding=3)
    , Image.from_text("non-Democrat/Republican candidates with highest popular vote share since 1860".upper(), arial(32), bg="white", padding=2)
    ], bg="white").pad((0,0,0,10), "white")

img = bar_chart(votes[["percent"]], 30, 1000, spacing=1, colors=color_fn, clabels={BarChartLabelPosition.OUTSIDE: ep_label_fn, BarChartLabelPosition.INSIDE: pc_label_fn, BarChartLabelPosition.AXIS: name_label_fn},
    ymin=0, ymax=0.301, label_interval=0.05, grid_interval=0.01, ylabels=arial(FONT_SIZE), yformat="{:.0%}", ylabel=ylabel, horizontal=True)
    
boxes = [Rectangle(56, c).place(Image.EMPTY_IMAGE if len(i) == 0 else Image.from_url_with_cache(i[0]).crop_to_aspect(1).resize_fixed_aspect(width=48)) for _,_,_,c,*i in LEGEND]
labels = [Image.from_column([
Image.from_text("{} [{}]".format(p, y), arial(16, bold=True), "black", "white"),
Image.from_text(d, arial(12), "black", "white", max_width=400, padding=(0,2))
], xalign=0) for p,y,d,_,*i in LEGEND]
legend = generate_legend(boxes, labels, header="By political party".upper(), spacing=0, fonts=papply(arial, 20))

img = Image.from_row([img, legend], bg="white", padding=10)
img = Image.from_column([title, img], bg="white", padding=(0,10))
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/politics_usthird.png")
