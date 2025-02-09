from pudzu.charts import *
from pudzu.pillar import *

FONT = sans
COLORS = {
    "Conservatives": "#393b79",
    "Labour": "#d62728",
    "Liberal Democrats": "#e7ba52", "Alliance": "#e7ba52", "Liberal": "#e7ba52",
    "Liberal Democrats/\nAlliance/Liberals": "#e7ba52",
    "SNP": "#FDF38E",
    "Reform": "#12B6CF",
    "UKIP": "#7b4173",
    "Greens": "#02A95B",
}
PARTIES = { v:k for k,v in COLORS.items() }
SHORT_NAMES = { "Liberal Democrats": "Lib Dems", "Conservatives": "Tories", "Liberal": "Liberals" }

def odds_ratio(a, b): return ((1-a) * b) / (a * (1-b))

df = pd.read_csv("datasets/ukelections2.csv")
totals = df[df.party=="TOTAL"].set_index("year")
df = df[df.party != "TOTAL"].reset_index(drop=True)
df['votes_pc'] = df.votes / totals.loc[df.year].reset_index().votes
df['seats_pc'] = df.seats / totals.loc[df.year].reset_index().seats
df['odds_ratio'] = odds_ratio(df['votes_pc'], df['seats_pc'])
df['leaning'] = np.where(df['odds_ratio']<1, df['odds_ratio']-1, 1-(1/df['odds_ratio']))
df['colors'] = df.party.map(COLORS)
df["winner"] = df.apply(lambda s: s.votes == df[df.year == s.year].votes.max(), axis=1)
df = df.sort_values("leaning", ascending=False).reset_index()

def color_fn(c, r, v): return df.colors[r]
def clabel_fn(c, r): return Image.from_text(
    f"{SHORT_NAMES.get(df.party[r],df.party[r])} {df.year[r]}".upper(),
    FONT(16, bold=True), align="center", line_spacing=1, padding=(5,0))

def clabel_pc(c, r, below=False):
    label = f"{df.votes_pc[r]:.1%} votes\n{df.seats_pc[r]:.1%} seats"
    display = (abs(df.leaning[r]) < 0.15) == below
    return Image.from_text(label, FONT(16, italics=True), align="center", line_spacing=0, padding=(2*below,0)) if display else None

def ylabel_fn(v):
    if v == 0: label= "proportional"
    else:
        direction = "under" if v < 0 else "over"
        factor = "∞" if abs(v) == 1 else "{0:.2g}".format(1 / (1 - abs(v)))
        label = "×{} {}".format(factor, direction)
    return Image.from_text(label, FONT(16), align="center")

ylabel = Image.from_text("level of (under-/over-)representation, based on the odds ratio of seats to votes: (seats / (total seats - seats)) / (votes / (total votes - votes))", FONT(24), padding=10, bg="white") #.transpose(Image.ROTATE_90)

bar = bar_chart(df[["leaning"]], 62, 1500, spacing=2, colors=color_fn, ymin=-1, ymax=1, grid_interval=0.125,
    horizontal=True,
    label_font=FONT(16), rlabels=None, clabels={
         BarChartLabelPosition.OUTSIDE : partial(clabel_pc, below=True),
         BarChartLabelPosition.INSIDE : partial(clabel_pc, below=False),
         BarChartLabelPosition.AXIS : clabel_fn,
}, ylabels=ylabel_fn, ylabel=ylabel)
legend = generate_legend(PARTIES.keys(), PARTIES.values(), 50, font_family=partial(FONT, 24), bg="#FFFFFF90",
                         header="POLITICAL PARTY", footer="Includes all parties with at least 5% vote or seat share.", max_width=300)
bar = bar.place(legend, 0, padding=(50,150)).pad((10,10), None)

title = Image.from_column([
     Image.from_text("Dis-proportional representation".upper(), FONT(72, bold=True), bg="white")
    , Image.from_text("winners and losers of the UK's first-past-the-post voting (1979–2024)".upper(), FONT(36), bg="white")
    ], bg="white", padding=(0, 5)).pad((0,0,0,10), "white")
img = Image.from_column([title, bar], bg="white")
#img.place(Image.from_text("/u/Udzu", FONT(16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/ukelections3.png")
