import sys
sys.path.append('..')
from charts import *

# get data
df = pd.read_html("https://en.wikipedia.org/wiki/Small_Arms_Survey")[0]
df = df.set_index(0).iloc[3:][[1]].rename(columns=lambda i: "weapons").update_columns(weapons=int)
countries = pd.read_csv("datasets/countries.csv").split_columns(('country'), "|").split_rows('country').set_index('country')

def get_name(c):
    for i in [c, strip_from(c, " ("), strip_from(c, ", "), strip_accents(c)]:
        if i in countries.index:
            return i
    if "United Kingdom" in c:
        return "UK"
    elif "Korea" in c:
        return ["North Korea", "South Korea"]["South" in c]
    else: 
        print(c)
        return None
    
def get_continent(c):
    return countries.continent.get(get_name(c), None)
    
def get_eu(c):
    return "eu" in get_non(countries.organisations, get_name(c), "")

df = df.assign_rows(continent=lambda r,i: get_continent(i), eu=lambda r,i: get_eu(i)).sort_values("weapons", ascending=False)

EUR = ("Europe", { "EU": df[df.eu == True].sum().weapons, "Russia": df.weapons["Russian Federation"] })
ASI = ("Asia", { k : df.weapons[k] for k in ("India", "China", "Pakistan", "Yemen") })
NAM = ("North America", { k : df.weapons[k] for k in ("United States of America", "Mexico", "Canada") })
SAM = ("South America", { k : df.weapons[k] for k in ("Brazil",) })
AFR = ("Africa", {})
OCE = ("Oceania", {})

data = []
labels = []
for c,d in [EUR, ASI, NAM, SAM, AFR, OCE]:
    rest = df[df.continent == c].weapons.sum() - sum(d.values())
    data.append([c, *[kv[1] for kv in sorted(d.items(), key=lambda kv: -kv[1])], rest])
    labels.append([c, *[kv[0] for kv in sorted(d.items(), key=lambda kv: -kv[1])], " "])
data = pd.DataFrame(data).fillna(0).set_index(0)
data = data.assign_rows(total=lambda d: sum(d)).sort_values("total", ascending=False).drop("total", axis=1)
labels = pd.DataFrame(labels).set_index(0)

# chart it
def rlabels(r):
    c = data.index[r]
    populations = { "Europe": 739, "Asia": 4436, "North America": 579, "Africa": 1216, "South America": 423,"Oceania": 40}
    return Image.from_markup("**{}**\n(pop. {:,}m)".format(c.upper(), populations[c]), partial(arial, 16), align="right").pad(5, "white")
    
def clabels(c,r,v,h,w):
    text = labels[c+1][data.index[r]]
    label = Image.from_text(text, arial(16))
    if (label.width*1.2 > w):
        label = Image.from_text(text, arial(16)).transpose(Image.ROTATE_270)
    return label
    
guns = bar_chart(data, 80, 1200, horizontal=True, spacing=2, type=BarChartType.STACKED,
    colors=lambda c,r,v: lambda sz: Rectangle(sz, VegaPalette10[r]).trim((1,0,1,0)).pad((1,0,1,0), "white"),
    clabels = {  BarChartLabelPosition.INSIDE: clabels }, label_font=arial(16),
    rlabels = rlabels, grid_interval=50000000, ymax=450000000, ylabels = lambda v: "{}M".format(v//1000000),
    ylabel=Image.from_text("estimated number of civilian held firearms (2017)", arial(18), padding=5))

# map it
def colorfn(c):
    if c in ['Sea', 'Borders']: return "white"
    elif c in ['United States']: return VegaPalette10.BLUE
    elif c in ['India']: return "#AAAAAA"
    else: return VegaPalette10.RED
worldmap = map_chart("maps/World.png", colorfn)
map_thumb = Image.from_column([
    worldmap,
    Image.from_text("two regions with a similar number of privately held firearms", arial(80, bold=True))
], bg="white", padding=10).resize_fixed_aspect(width=500).pad(5, "white")
chart = guns.place(map_thumb, (1, 1), padding=(40,20))

# title it
title = Image.from_column([Image.from_text("Civilian held firearms worldwide".upper(), arial(64, bold=True)), Image.from_text("as estimated by the Small Arms Survey 2018", arial(56, italics=True))])
img = Image.from_column([title, chart], padding=5, bg="white").pad((0,0,0,50), "white")
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg=None, padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/politics_guns.png")

