import seaborn as sns
from pudzu.charts import *
from pudzu.bamboo import *

# -----------------------------
# European Nobel prizes winners
# -----------------------------

SIZE = 50
CMAP = sns.cubehelix_palette(start=.5, rot=-.75, as_cmap=True)
CATS = ["Physics", "Chemistry", "Physiology and Medicine", "Literature", "Peace", "Economics" ]
CATPAL = sns.color_palette("colorblind")
PALETTE = { cat : RGBA(col) for cat,col in zip(CATS, CATPAL) }
NONNATIVE = "#EEEEAA"
NOPRIZE = "#EEEEEE"

tiles = pd.read_csv("maps/europe_tiles.csv", names=range(15)).as_matrix()
generate_tile_map(tiles, "cache/europe_tiles_map.png", SIZE)

countries = pd.read_csv("datasets/countries.csv").split_columns(('nationality', 'tld', 'country'), "|").split_rows('tld').update_columns(tld=lambda v: v[1:]).set_index('tld')
nobels = pd.read_csv("datasets/nobels.csv").split_columns('countries', '|').split_rows('countries')
# .assign_rows(countries=lambda d: set(d['countries'] + (d['birthplace'],)))
bycountry = nobels.groupby(('countries', 'category')).count()['name']

# tile map

def colorfn(c):
    if not isinstance(c, str): return None
    cname = first(cname for cname in countries['country'][c] if cname in bycountry)
    if cname:
        n = bycountry[cname].sum()
        nobelspermil = n * 1000000 / countries['population'][c]
        color = tmap(RGBA, CMAP(nobelspermil / 5))
    else:
        cname = first(cname for cname in countries['country'][c] if cname in nobels.groupby('birthplace').count()['name'])
        color = NONNATIVE if cname else NOPRIZE
    return color
    
def labelfn(c):
    if not isinstance(c, str): return None
    color = colorfn(c)
    cname = first(cname for cname in countries['country'][c] if cname in bycountry)
    n = 0 if cname not in bycountry else bycountry[cname].sum()
    name = Image.from_text(c, arial(16,bold=True), fg="black", bg=color, padding=1)
    winners = sorted(Counter(bycountry[cname].to_dict()).elements(), key=lambda v: CATS.index(v)) if n > 0 else []
    boxes = Image.from_array([[Image.new("RGBA", (SIZE//10-2,SIZE//10-2), PALETTE[winners[10*y+x]]).pad(1, 0) if 10*y+x < n else None for x in range(10)] for y in range(15)])
    return Image.from_column([name.pad((0,0,0,4),0), boxes])
    
grid = map_chart("cache/europe_tiles_map.png", colorfn, labelfn)

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
gradimg = Image.from_column([gradimg, 
Image.from_row([Image.new("RGBA", (GW,GW), NONNATIVE), Image.from_text("local-born\nforeign nationals", arial(14), fg="black", bg="white", padding=(5,0,0,3))], bg="white")
], bg="white", xalign=0)
gradleg = Image.from_column([Image.from_text("Prizes per capita", arial(16, bold=True)), gradimg], bg="white", xalign=0, padding=(0,5))

catimg = Image.from_array([[Image.new("RGBA", (GW,GW), PALETTE[cat]), Image.from_text(cat, arial(14), padding=(5,0,0,0), max_width=100)] for cat in CATS], xalign=0, bg="white")
catleg = Image.from_column([Image.from_text("Prize categories", arial(16, bold=True)), catimg], bg="white", xalign=0, padding=(0,5))

legend = Image.from_column([gradleg, catleg], bg="white", xalign=0, padding=5).pad(1, "black")
gridleg = Image.from_row([grid, legend.pad((50,0,0,5), "white")], yalign=0, bg="white")

# put it all together

title = Image.from_column([
Image.from_text("European Nobel laureates by nationality", arial(48, bold=True), fg="black", bg="white", padding=(0,20,0,0)),
Image.from_text("using modern countries of citizenship, based on Wikipedia", arial(24, bold=True), fg="black", bg="white", padding=(0,0,0,40))
], bg="white")
chart = Image.from_column([title, gridleg], bg="white").pad(5,"white")
# chart.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=0, copy=False)
chart.save("output/nobels_mapeu.png")
