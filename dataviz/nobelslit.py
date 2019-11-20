import seaborn as sns
from pudzu.charts import *
from pudzu.bamboo import *

countries = pd.read_csv("datasets/countries.csv")[["country", "continent", "flag"]].split_columns('country', "|").explode('country').set_index('country')

df = pd.read_csv("datasets/nobels.csv")
df = df[df['category'] == "Literature"][["name", "countries"]].split_columns("countries", "|")
df = df.assign_rows(continents=lambda r: tuple(sorted(set(countries.continent[c] for c in r.countries))))

NORDIC = ["Iceland", "Finland", "Sweden", "Norway", "Denmark"]
nordic_counts = df.update_columns(countries=lambda cs: tuple(sorted(set(c for c in cs if c in NORDIC)))).filter_rows(lambda r: any(r.countries)).groupby("countries").count().name
continent_counts = df.groupby("continents").count().name
counts = pd.concat((nordic_counts, continent_counts))

# chart

categories = { "Old World": ["Asia", "Africa"], "New World": ["South America", "North America", "Oceania"], "Europe": ["Europe"], "Nordic": NORDIC }
catlabels = { "Europe": "Europe (740m)", "New World": "Americas & Oceania (1,040m)", "Old World": "Asia & Africa (5,650m)", "Nordic": "Nordic countries (27m)" }

table = pd.DataFrame([{subcat: counts[subcat] if any(c in subcat for c in categories[cat]) else 0 for subcat in counts.index } for cat in categories], index=categories)
table = table.assign_rows(sum=lambda r: r.sum()).sort_values("sum", ascending=False).drop("sum", axis=1)
table = table[[ # hack #1 to get nice ordering
("Sweden",), ("Denmark",), ("Norway",), ("Finland",), ("Iceland",),
("Europe",),
("North America",), ("Europe", "North America"),
("Asia",), ("Asia", "Europe"),
("South America",), ("Europe", "South America"),
("Europe", "Oceania"),
("Africa",), ("Africa", "Europe"), ("Africa", "Oceania")
]]

WIDTH = 80
BAR = 3

PALETTE = tmap(RGBA, sns.xkcd_palette(["windows blue", "faded green", "amber", "dusty purple", "red", "brown"]))
CONTINENTS = [ "Europe", "North America", "South America",  "Oceania", "Asia","Africa" ]
def continent_colour(c):
    return PALETTE[CONTINENTS.index(c)]

def stripe(c1, c2=None):
    if c2 is None: c2 = c1
    return Image.from_column([Image.new("RGBA", (100,BAR), c1), Image.new("RGBA", (100,BAR), c2)])

def stripe_pattern(height, c1, c2=None):
    return Image.from_pattern(stripe(c1, c2), (WIDTH,height))

def colorfn(c,r):
    cs = table.columns[c] if isinstance(c, int) else (c,)
    if len(cs) == 2 and cs[0] not in categories[table.index[r]]: cs = cs[1], cs[0]
    if any(c in CONTINENTS for c in cs):
        return lambda size: stripe_pattern(size[1], *[continent_colour(c) for c in reversed(cs)])
    flagcolors = sorted(Image.from_url_with_cache(countries.flag[cs[0]]).convert("RGBA").getcolors(), reverse=True)
    return lambda size: Image.from_row([Image.new("RGBA", (16, size[1]), flagcolors[0][1]),
                                       Image.new("RGBA", (8, size[1]), flagcolors[1][1]),
                                       Image.new("RGBA", (WIDTH-16-8, size[1]), flagcolors[0][1])])
                           
def rlabelfn(r):
    return Image.from_text(catlabels[table.index[r]], arial(14, bold=False), "black", "white", align="center", padding=2, max_width=WIDTH)
    
ymax = 100
chart = bar_chart(table, WIDTH, BAR*2*ymax, type=BarChartType.STACKED, spacing=10, colors=colorfn, grid_interval=10, tick_interval=5, label_font=arial(14), rlabels=rlabelfn, bg="white", fg="black", ylabel=Image.from_text("# Nobel Literature laureates", arial(14), padding=(0,2,0,10), bg="white").transpose(Image.ROTATE_90), ymax=ymax, clabels=None)

def lbox(c):
    count = counts.select(lambda cs: c in cs).sum()
    box = colorfn(c, 0)((WIDTH,WIDTH)).resize_fixed_aspect(width=BOXSIZE)
    return box.place(Image.from_text(str(count), arial(14), "black" if c == "Finland" else "white"))

BOXSIZE = 30
cboxes = [[lbox(c), Image.from_text(c, arial(14), padding=(5,0), fg="black", bg="white")] for c in CONTINENTS]
clegs = Image.from_array(cboxes, bg="white", xalign=0)
nboxes = [[lbox(c), Image.from_text(c, arial(14), padding=(5,0), fg="black", bg="white")] for c in sorted(NORDIC)]
nlegs = Image.from_array(nboxes, bg="white", xalign=0)
legend = Image.from_column([
Image.from_text("Continents", arial(14, bold=True)),
clegs,
Image.from_text("(stripes indicate winners with dual nationalities)", arial(14), max_width=150, padding=(0,0,0,10)),
Image.from_text("Countries", arial(14, bold=True)),
nlegs
], bg="white", padding=(0,3), xalign=0).pad(5, "white").pad(1, "black")

chart = Image.from_row([chart, legend], bg="white", yalign=0, padding=5)
title = Image.from_text("Geographic distribution of Literature Nobel laureates", arial(24, bold=True)).pad((0,4,0,8), "white")
img = Image.from_column([title, chart], bg="white")
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/nobels_lit.png")
