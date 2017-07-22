import sys
sys.path.append('..')
from charts import *

# -------------------------
# Periodic table grid chart
# -------------------------

W, H = 220, 100 # cell dimensions excluding 1px border
PALETTE = ["#c3dcee", "#c9c8d8", "#eac8ea", "#f9b4b7", "#fdd8b0", "#fffcbf", "#cdecd2", "#d8d8d8"]
SAMPLE = {"Z": "number", "name": "Element", "symbol": "El", "year": "date", "countries": ["un"], "types": "etymology", "group": -1}
DATERANGES = (1600,1800,1850,1900,1950,2000,2050)

# load records
rs = RecordCSV.load_file("periodic.csv", delimiter="\t", array_separator=",")
@artial(ignoring_exceptions, -1, KeyError)
@artial(ignoring_exceptions, 0, ValueError)
def year_group(d): return next(i+1 for i,x in enumerate(DATERANGES) if int(d['year']) < x)
rs = update_records(rs, update_with(group=year_group))

# generate flag urls
try:
    flags = { d['country'] : d['flag'] for d in RecordCSV.load_file("periodic_flags.csv") }
except:
    from wikipage import *
    countrynames = { 'se': 'Sweden', 'uk': 'UK', 'de': 'Germany', 'dk': 'Denmark', 'fr': 'France', 'mx': 'Mexico', 'fi': 'Finland', 'ru': 'Russia', 'it': 'Italy', 'at': 'Austria', 'us': 'United States', 'ch': 'Switzerland', 'es': 'Spain', 'jp': 'Japan', 'ca': 'Canada', 'pl': 'Poland' }
    flags = { k : WikiPage("Flag of {}".format(v)).image_url for k,v in countrynames.items() }
    flags['un'] = 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Flag_of_the_United_Nations.svg/1024px-Flag_of_the_United_Nations.svg.png'
    RecordCSV.save_file("periodic_flags.csv", map_to_records(flags, "country", "flag"))
countries = {c for d in rs for c in d.get('countries',[])} | {'un'}
assert(countries == set(list(flags)))

# generate main grid
def table_cell(d):
    if d is None: return Image.new("RGBA", (W+2,H+2), "white")
    c = PALETTE[d['group']]
    cbg = ImageColor.getrgba(c)._replace(alpha=0)
    flagbase = Image.new("RGBA", (W,H), c)
    n = len(d.get('countries',[]))
    flag = flagbase if n == 0 else Image.from_row([Image.from_url_with_cache(flags[d['countries'][i]]).resize((W//n,H)) for i in range(n)])
    flag = Image.blend(flagbase, flag.convert("RGBA"), 0.8)
    flag = flag.place(Image.from_text(d['symbol'], arial(48,bold=True), fg="black"))
    year = Image.new("RGBA", (W,H//2), c)
    year = year.place(Image.from_text(d.get('year'," "), arial(24,bold=True), fg="black", bg=cbg), align=(0,0.5),padding=(5,0))
    if d == SAMPLE:
        year = year.place(Image.from_text(d['types'], arial(24,bold=True), fg="black", bg=cbg), align=(1,0.5),padding=(5,0))
    elif 'types' in d:
        types = Image.from_row([Image.open("icons/{}.png".format(t)).resize_fixed_aspect(width=30).convert("RGBA") for t in d['types']], padding=2, bg=cbg)
        year = year.place(types, align=(1,0.5), padding=(5,0))
    name = Image.new("RGBA", (W,H//2), c)
    name = name.place(Image.from_text(d.get('name'," "), arial(24,bold=True), fg="black", bg=cbg), align=(0,0.5),padding=(5,0))
    name = name.place(Image.from_text(d.get('Z'," "), arial(24,bold=True), fg="black", bg=cbg), align=(1,0.5),padding=(5,0))
    return Image.from_column([year, flag, name]).pad(1, "black")
    
table = tabulate_records(rs, col_group_by="x", columns=range(1,max(d['x'] for d in rs)+1),
                             row_group_by="y", rows=range(1,max(d['y'] for d in rs)+1),
                             fn=first_or_none)
grid = grid_chart(table, table_cell, bg="white")
    
# legends
GLABELS = ["premodern", "1650–1799", "1800–1849", "1850–1899", "1900–1949", "1950–1999", "2000–present"]
CLABELS = {"uk": "UK", "se": "Sweden", "fr": "France", "de": "Germany", "ru": "Russia/USSR", "us": "US", "other": "Other" }
TLABELS = ["color", "myth", "person", "place"]

gdata = tabulate_records(rs, rows=["value"], col_group_by="group", columns=range(0,7))
cgroup = group_records(rs, group_by=lambda d: ["other" if c not in CLABELS else c for c in d.get("countries",[])])
cgroup = sorted_groups(cgroup, group_key=lambda g,v: -1 if g=="other" else len(v), group_reverse=True)
cdata = tabulate_groups(cgroup, subgroups=["value"], transpose=True)
tdata = tabulate_records(rs, rows=["value"], col_group_by="types", columns=TLABELS)

def make_legend(array, title):
    aimg = Image.from_array(array, xalign=(0.5,0), padding=(5,6), bg="white")
    return Image.from_column([Image.from_text(title, arial(36, bold=True), "black").pad((7,0,0,10),"white"), aimg], xalign=0, bg="white").pad(12,"white").pad(2)
        
def glegend_entry(i, s):
    box = Image.new("RGBA", (50,40), PALETTE[i]).place(Image.from_text(str(gdata[i]["value"]), arial(24), "black", bg=PALETTE[i]))
    label = Image.from_text(s, arial(32), "black", bg="white")
    return [box, label]
glegend = make_legend([glegend_entry(i, s) for i,s in enumerate(GLABELS)], "by date")

def clegend_entry(c):
    box = Image.from_url_with_cache(flags["un" if c == "other" else c]).resize((50,40))
    label = Image.from_text("{} ({})".format(CLABELS[c], cdata[c]["value"]), arial(32), "black", bg="white")
    return [box, label]
clegend = make_legend([clegend_entry(c) for c in cdata.columns], "by country")

def tlegend_entry(t):
    box = Image.open("icons/{}.png".format(t)).resize_fixed_aspect(width=50).convert("RGBA")
    label = Image.from_text("{} ({})".format(t, tdata[t]["value"]), arial(32), "black", bg="white")
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
img.save("periodic.png")
