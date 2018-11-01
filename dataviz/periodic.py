from pudzu.charts import *
from pudzu.bamboo import *

# -------------------------
# Periodic table grid chart
# -------------------------

W, H = 220, 100 # cell dimensions excluding 1px border
PALETTE = ["#c3dcee", "#c9c8d8", "#eac8ea", "#f9b4b7", "#fdd8b0", "#fffcbf", "#cdecd2", "#d8d8d8"]
SAMPLE = {"Z": "number", "name": "Element", "symbol": "El", "year": "date", "countries": ["un"], "types": "etymology", "group": -1}
DATERANGES = (1600,1800,1850,1900,1950,2000,2050)

# load data
df = pd.read_csv("datasets/periodic.csv").split_columns(('countries', 'types'), "|")
@artial(ignoring_exceptions, -1, KeyError)
@artial(ignoring_exceptions, 0, ValueError)
def year_group(d): return -1 if non(d['year']) else next(i for i,x in enumerate(DATERANGES) if int(d['year']) < x)
df = df.assign_rows(group=year_group)

# load flag urls
atlas = pd.read_csv("datasets/countries.csv").split_columns(('nationality', 'tld', 'country'), "|")
flags = { tld[1:] : d['flag'] for _,d in atlas.iterrows() for tld in d['tld'] }
flags['un'] = 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Flag_of_the_United_Nations.svg/1024px-Flag_of_the_United_Nations.svg.png'
countries = {c for _,d in df.iterrows() for c in d['countries']} | {'un'}
assert(countries <= set(list(flags)))

# generate main grid
def table_cell(d):
    if d is None: return Image.new("RGBA", (W+2,H+2), "white")
    c = PALETTE[d['group']]
    cbg = RGBA(c)._replace(alpha=0)
    flagbase = Image.new("RGBA", (W,H), c)
    n = len(d['countries'])
    flag = flagbase if n == 0 else Image.from_row([Image.from_url_with_cache(flags[d['countries'][i]]).resize((W//n,H)) for i in range(n)])
    flag = Image.blend(flagbase, flag.convert("RGBA"), 0.8)
    flag = flag.place(Image.from_text(d['symbol'], arial(48,bold=True), fg="black"))
    year = Image.new("RGBA", (W,H//2), c)
    year = year.place(Image.from_text(get_non(d,'year'," "), arial(24,bold=True), fg="black", bg=cbg), align=(0,0.5),padding=(5,0))
    if d == SAMPLE:
        year = year.place(Image.from_text(d['types'], arial(24,bold=True), fg="black", bg=cbg), align=(1,0.5),padding=(5,0))
    elif len(d['types']) > 0:
        types = Image.from_row([Image.open("icons/{}.png".format(t)).resize_fixed_aspect(width=30).convert("RGBA") for t in d['types']], padding=2, bg=cbg)
        year = year.place(types, align=(1,0.5), padding=(5,0))
    name = Image.new("RGBA", (W,H//2), c)
    name = name.place(Image.from_text(get_non(d,'name'," "), arial(24,bold=True), fg="black", bg=cbg), align=(0,0.5),padding=(5,0))
    name = name.place(Image.from_text(get_non(d,'Z'," "), arial(24,bold=True), fg="black", bg=cbg), align=(1,0.5),padding=(5,0))
    return Image.from_column([year, flag, name]).pad(1, "black")
  
# df.x.max()
table = pd.DataFrame([[first([dict(d) for _,d in df[(df.x == x) & (df.y == y)].iterrows()]) for x in range(1,df.x.max()+1)] for y in range(1,df.y.max()+1)])

grid = grid_chart(table, table_cell, bg="white")
    
# legends
GLABELS = ["premodern", "1650–1799", "1800–1849", "1850–1899", "1900–1949", "1950–1999", "2000–present"]
CLABELS = {"uk": "UK", "se": "Sweden", "fr": "France", "de": "Germany", "ru": "Russia/USSR", "us": "US", "other": "Other" }
TLABELS = ["color", "myth", "person", "place"]

gdata = df.groupby('group').count().Z
cdata = df.split_rows('countries').update_columns(countries=lambda v: v if v in CLABELS else 'other').groupby('countries').count().Z
tdata = df.split_rows('types').groupby('types').count().Z

def make_legend(array, title):
    aimg = Image.from_array(array, xalign=(0.5,0), padding=(5,6), bg="white")
    return Image.from_column([Image.from_text(title, arial(36, bold=True), "black").pad((7,0,0,10),"white"), aimg], xalign=0, bg="white").pad(12,"white").pad(2, "black")
        
def glegend_entry(i, s):
    box = Image.new("RGBA", (50,40), PALETTE[i]).place(Image.from_text(str(gdata[i]), arial(24), "black", bg=PALETTE[i]))
    label = Image.from_text(s, arial(32), "black", bg="white")
    return [box, label]
glegend = make_legend([glegend_entry(i, s) for i,s in enumerate(GLABELS)], "by date")

def clegend_entry(c):
    box = Image.from_url_with_cache(flags["un" if c == "other" else c]).resize((50,40))
    label = Image.from_text("{} ({})".format(CLABELS[c], cdata[c]), arial(32), "black", bg="white")
    return [box, label]
clegend = make_legend([clegend_entry(c) for c in sorted(CLABELS, key=lambda c: (0 if c=='other' else cdata[c], CLABELS[c]), reverse=True)], "by country")

def tlegend_entry(t):
    box = Image.open("icons/{}.png".format(t)).resize_fixed_aspect(width=50).convert("RGBA")
    label = Image.from_text("{} ({})".format(t, tdata[t]), arial(32), "black", bg="white")
    return [box, label]
tlegend = make_legend([tlegend_entry(t) for t in TLABELS], "by etymology")
    
legends = Image.from_row([table_cell(SAMPLE), glegend, clegend, tlegend], yalign=0, padding=(50,0), bg="white")
grid.overlay(legends, ((W+2)*4-100,(H+2)*2-150))

# title, footer and sig
title = Image.from_column([
            Image.from_text("THE PERIODIC TABLE", arial(120, bold=True), "black", bg="white"),
            Image.from_text("with country and date of discovery", arial(60), "black", "white")], bg="white", padding=5)
footer = Image.from_text("*dates, discoverers, etymologies and flags all from Wikipedia; etymology icons by SimpleIcon and Freepik from www.flaticon.com, licensed by CC 3.0 BY.", arial(36), "black", "white")
img = Image.from_column([title, grid, footer], bg="white", padding=50)
img = img.place(Image.from_text("/u/Udzu", font("arial", 36), fg="black", bg="white", padding=15).pad((2,2,0,0), "black"), align=1)
img.save("output/periodic.png")
