import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np
from pudzu.charts import *

FONT = sans
COLORS = {
    "Conservatives": "#393b79",
    "Labour": "#d62728",
    "Liberal Democrats": "#e7ba52", "Alliance": "#e7ba52", "Liberal": "#e7ba52",
    "Liberal Democrats/\nAlliance/Liberals": "#e7ba52",
    "SNP": "#FDF38E",
    "UKIP": "#7b4173",
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
df = df.sort_values("leaning").reset_index()

def color_fn(c, r, v): return df.colors[r]
def clabel_fn(c, r): return f"{SHORT_NAMES.get(df.party[r],df.party[r])}\n{df.year[r]}"
def clabel_pc(c, r, below=False):
    label = f"{df.votes_pc[r]:.1%} vs\n{df.seats[r]} seat" + "s"*(df.seats[r]>1)
    display = (abs(df.leaning[r]) < 0.05) == below
    return label if display else None

def ylabel_fn(v):
    if v == 0: return "proportional"
    direction = "under" if v < 0 else "over"
    factor = "∞" if abs(v) == 1 else "{0:.2g}".format(1 / (1 - abs(v)))
    return "×{} {}".format(factor, direction)

ylabel = Image.from_text("level of (under-/over-)representation, based on the odds ratio of votes to seats", FONT(24), padding=5, bg="white").transpose(Image.ROTATE_90)

bar = bar_chart(df[["leaning"]], 62, 1000, spacing=2, colors=color_fn, ymin=-1, ymax=1, grid_interval=0.125, 
    label_font=FONT(12), rlabels=None, clabels={
         BarChartLabelPosition.OUTSIDE : clabel_fn,
         BarChartLabelPosition.INSIDE : partial(clabel_pc, below=False),
         BarChartLabelPosition.AXIS : partial(clabel_pc, below=True)
}, ylabels=ylabel_fn, ylabel=ylabel)
legend = generate_legend(PARTIES.keys(), PARTIES.values(), font_family=partial(FONT, 16), header="POLITICAL PARTY", footer="Includes all parties with at least 5% vote or seat share.", max_width=200)
bar = bar.place(legend, 0, padding=(150,50))

title = Image.from_column([
     Image.from_text("Dis-proportional representation".upper(), FONT(60, bold=True), bg="white")
    , Image.from_text("winners and losers of the UK's first-past-the-post voting (1979–2019)".upper(), FONT(32), bg="white")
    ], bg="white", padding=(0, 5)).pad((0,0,0,10), "white")
img = Image.from_column([title, bar], bg="white")
img.place(Image.from_text("/u/Udzu", FONT(16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/ukelections3.png")
