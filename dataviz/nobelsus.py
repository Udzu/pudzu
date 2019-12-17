import seaborn as sns
from pudzu.charts import *
from pudzu.experimental.bamboo import *

# ------------------------
# Nobel prizes by US state
# ------------------------

SIZE = 100
CMAP = sns.cubehelix_palette(start=.5, rot=-.75, as_cmap=True)
CATS = ["Physics", "Chemistry", "Physiology and Medicine", "Literature", "Peace", "Economics" ]
CATPAL = sns.color_palette("colorblind")
PALETTE = { cat : RGBA(col) for cat,col in zip(CATS, CATPAL) }

nobels = pd.read_csv("datasets/nobels.csv").split_columns('countries', '|').update_columns(birthplace=lambda v: 'UK' if v.startswith('UK') else v)
uswinners = nobels[nobels.countries.map(lambda cs: 'US' in cs)].groupby(('birthplace', 'category')).count()['countries']

# US-born winners

states = pd.read_csv("datasets/usstates.csv")[lambda df: df.code != 'PR']
statetable = pd.DataFrame([[first([dict(d) for _,d in states[(states.grid_x == x) & (states.grid_y == y)].iterrows()]) for x in range(states.grid_x.max()+1)] for y in range(states.grid_y.max()+1)])

def statecell(d):
    W, H = SIZE+4, SIZE+4
    if d is None: return Image.new("RGBA", (W,H), "white").pad(1, "white")
    code = "US_" + d['code']
    nobels = 0 if code not in uswinners else uswinners[code].sum()
    nobelspermil = nobels * 1000000 / d['population']
    winners = sorted(Counter(uswinners[code].to_dict()).elements(), key=lambda v: CATS.index(v)) if nobels > 0 else []
    color = tmap(RGBA, CMAP(nobelspermil / 5)) if nobels > 0 else "#EEEEEE"
    img = Image.new("RGBA", (W,H), color)
    name = Image.from_text("{}".format(d['code']), arial(24,bold=True), fg="black", bg=color)
    boxes = Image.from_array([[Image.new("RGBA", (SIZE//10-2,SIZE//10-2), PALETTE[winners[10*y+x]]).pad(1, 0) if 10*y+x < nobels else None for x in range(10)] for y in range(10)])
    img = img.place(Image.from_column([name.pad((0,0,0,8), bg=0), boxes]))
    img = img.pad(1, "white")
    return img

stategrid = grid_chart(statetable, statecell, bg="white")

# foreign-born winners

flags = pd.read_csv("datasets/countries.csv").split_columns(('nationality', 'tld', 'country'), "|").explode('country').set_index('country')['flag']
foreignplaces = sorted(((-uswinners[c].sum(), c) for c in uswinners.index.levels[0] if not c.startswith("US_")))
foreigntable = pd.DataFrame([[foreignplaces[12*y+x][1] if 12*y+x < len(foreignplaces) else None for x in range(12)] for y in range(3)])

def foreigncell(c):
    W, H = SIZE + 4, (SIZE+4)*3//4
    if c is None: return Image.new("RGBA", (W,H), "white").pad(1, "white")
    nobels = uswinners[c].sum()
    winners = sorted(Counter(uswinners[c].to_dict()).elements(), key=lambda v: CATS.index(v))
    img = Image.new("RGBA", (W,H), RGBA(CMAP(0.0)))
    flag = Image.from_url_with_cache(flags[c]).resize((W,H))
    img = Image.blend(img, flag.convert("RGBA"), 0.1)
    name = Image.from_text(c, arial(16,bold=True), fg="black")
    boxes = Image.from_array([[Image.new("RGBA", (SIZE//10-2,SIZE//10-2), PALETTE[winners[10*y+x]]).pad(1, 0) if 10*y+x < nobels else None for x in range(10)] for y in range(10)])
    img = img.place(Image.from_column([name.pad((0,0,0,8), bg=0), boxes]))
    img = img.pad(1, "white")
    return img

foreigngrid = grid_chart(foreigntable, foreigncell, bg="white")

# legend

GW, GH = 40, 200

gradarray = np.fromfunction(lambda y, x: 1 - (y / GH), (GH, GW), dtype=float)
gradimg = Image.fromarray(CMAP(gradarray, bytes=True)).pad((0,0,0,1))
griddraw = ImageDraw.Draw(gradimg)
for i in range(0,6):
    griddraw.line([(0, GH * (5-i) // 5), (GW, GH * (5-i) // 5)], fill="#333333")
for i in range(0,6):
    label = Image.from_text("{}{} per million".format(i, "" if i < 5 else "+"), arial(14), fg="black", bg="white", padding=(5,0,0,0))
    gradimg = gradimg.pin(label, (GW, GH * (5-i) // 5), align=(0,0.5), bg="white")
gradleg = Image.from_column([Image.from_text("Prizes per capita", arial(16, bold=True)), gradimg], bg="white", xalign=0, padding=(0,5))

catdict = nobels[nobels.countries.map(lambda cs: 'US' in cs)].groupby('category').count()['countries']
def catbox(cat):
    img = Image.new("RGBA", (GW,GW), PALETTE[cat])
    img = img.place(Image.from_text(str(catdict[cat]), arial(14), "black", bg=PALETTE[cat]))
    return img
catimg = Image.from_array([[catbox(cat), Image.from_text(cat, arial(14), padding=(5,0,0,0), max_width=100)] for cat in CATS], xalign=0, bg="white")
catleg = Image.from_column([Image.from_text("Prize categories", arial(16, bold=True)), catimg], bg="white", xalign=0, padding=(0,5))

legend = Image.from_column([gradleg, catleg], bg="white", xalign=0, padding=5).pad(1, "black") # TODO: "countries of birth based on modern borders"
grid = Image.from_column([stategrid, foreigngrid.pad((0,50,0,0), "white")], padding=5, bg="white")
gridleg = Image.from_row([grid, legend.pad((50,150,0,5), "white")], yalign=0, bg="white")

# chart

title = Image.from_column([
Image.from_text("U.S. Nobel laureates by place of birth", arial(60, bold=True), fg="black", bg="white", padding=(0,20,0,0)),
Image.from_text("(state or country of birth, based on modern borders)", arial(36, bold=True), fg="black", bg="white", padding=(0,0,0,40))
], bg="white")
chart = Image.from_column([title, gridleg], bg="white")
chart.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
chart.save("output/nobels_mapus.png")
