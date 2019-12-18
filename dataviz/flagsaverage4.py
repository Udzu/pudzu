from pudzu.charts import *
from pudzu.sandbox.bamboo import *
import scipy.stats

df = pd.read_csv("../dataviz/datasets/countries.csv").filter_rows("organisations >> un").split_columns('country', "|").explode('country').set_index('country').drop_duplicates(subset='flag', keep='first')

wf = pd.read_html("https://en.wikipedia.org/wiki/List_of_countries_and_dependencies_by_area")[0]
wf = wf.rename(columns=wf.iloc[0])[1:].fillna("0")
wf = wf.assign_rows(country=lambda d: d[next(c for c in wf.columns if "state" in c)].split(" (")[0].split(" !")[-1].strip(" \xa0"))
wf = wf.assign_rows(area=lambda d: float(d[next(c for c in wf.columns if "Total" in c)].split(" (")[0].split("(")[0].split(chr(9824))[-1].replace(",","").replace("<","")))
wf = wf.drop_duplicates("country", "last").set_index("country")
wf.area["Micronesia"] = wf.area["Federated States of Micronesia"]
df = df.assign_rows(area=lambda d,c: wf.area.get(c) or wf.area[c.split(" ")[-1]])

class HeraldicPalette(metaclass=NamedPaletteMeta):
    OR = "#fcdd09"
    ARGENT = "#ffffff"
    AZURE = "#0f47af"
    GULES = "#da121a"
    PURPURE = "#9116a1"
    SABLE = "#000000"
    VERT = "#009200"
    TENNE = "#804000"
    ORANGE = "#ff8000"
    CELESTE = "#75aadb"

def flag_image(c):
    return Image.from_url_with_cache(df.flag[c]).convert("RGBA").remove_transparency("white").to_palette(HeraldicPalette).convert("RGBA")

def histogram(c):
    img = flag_image(c)
    cols = { next(n for n,p in zip(HeraldicPalette.names, HeraldicPalette) if RGBA(c) == p) : v for v,c in img.getcolors() }
    return valmap(lambda v: v / sum(cols.values()), cols)

df['histogram'] = [histogram(c) for c in df.index]

def by_country(i, r, c): return [1,0][c == "Asia"] if i == "Russia" and c is not None else 1
def by_population(i, r, c): return [110000000,35000000][c == "Asia"] if i == "Russia" and c is not None else r.population
def by_area(i, r, c):return [4275000,12825000][c == "Asia"] if i == "Russia" and c is not None else r.area
    
def averaged(continent=None, weight=by_area):
    histograms = [valmap(lambda v: v*weight(c, r, continent), r.histogram) for c,r in df.iterrows() if continent is None or r.continent == continent or c == "Russia" and continent == "Asia"]
    average = merge_dicts(*histograms, merge_fn=lambda k,*vs: sum(vs))
    average = valmap(lambda v: v / sum(average.values()), average)
    average = sorted(average.items(), key=lambda s: -s[1] if continent is None else order.index(s[0]))
    return average

order = [x[0] for x in averaged()]

def diff_histograms(h1, h2):
    return sum(abs(h1.get(c,0) - h2.get(c,0)) for c in HeraldicPalette.names)
    
def closest(continent=None):
    rows = [cr for cr in df.iterrows() if continent is None or cr[1].continent == continent]
    average = dict(averaged(continent))
    return min(rows, key=lambda cr: diff_histograms(cr[1].histogram, average))[0]
    
def label_image(text, align="center"):
    return Image.from_text(text.upper().replace(" ","\n"), LABEL_FONT, "black", "white", align=align)

labels = [None, Image.from_text("combined flag colors".upper(), calibri(24)), Image.from_text("closest flag".upper(), calibri(24))]
array = [[Image.from_text((continent or "World").upper(), calibri(24)),
          Image.from_gradient(PaletteColormap(*[HeraldicPalette[x[0]] for x in average], intervals=[x[-1] for x in average]), (600,100)).trim(1).pad(1, "black"),
          flag_image(closest(continent)).resize((150,100)).trim(1).pad(1, "black"),
          Image.from_text(closest(continent).upper(), calibri(24))]
          for continent in [None, "Asia", "Africa", "Europe", "North America", "South America", "Oceania" ]
          for average in [averaged(continent)]]
grid = Image.from_array(array, padding=5, bg="white", xalign=(1,0.5,0.5,0))

allflags = [Image.from_url_with_cache(df.flag[c]).convert("RGBA").resize((30,20)) for c in sorted(df.index)]
allflags = Image.from_array(list(generate_batches(allflags, 28)))

title = Image.from_text("Most representative flag (weighted)".upper(), calibri(48, bold=True))
label1 = Image.from_text("calculated by combining the colors of all the relevant flags, weighted by area:", calibri(24, italics=True))
label2 = Image.from_text("quantizing them to heraldic colors:", calibri(24, italics=True))
checkers = Checkers((40*len(HeraldicPalette), 40), GradientColormap(*HeraldicPalette), shape=(len(HeraldicPalette), 1), colors=len(HeraldicPalette)).add_grid((len(HeraldicPalette), 1))
label3 = Image.from_text("and then finding the flag with the most similar color composition.", calibri(24, italics=True))

img = Image.from_column([title, label1, allflags, label2, checkers, label3, Rectangle((0,20)), grid], padding=5, bg="white")
img.save("output/flagsaverage4_area.png")
