from pudzu.charts import *
from pudzu.bamboo import *
import scipy.stats

df = pd.read_csv("../dataviz/datasets/countries.csv").filter_rows("organisations >> un").split_columns('country', "|").split_rows('country').set_index('country').drop_duplicates(subset='flag', keep='first')
order = ['GULES', 'ARGENT', 'AZURE', 'VERT', 'OR', 'CELESTE', 'SABLE', 'TENNE', 'ORANGE', 'PURPURE']

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

def averaged(continent=None, weighted=False):
    histograms = [valmap(lambda v: v*(r.population if weighted else 1), r.histogram) for _,r in df.iterrows() if continent is None or r.continent == continent]
    average = merge_dicts(*histograms, merge_fn=lambda k,*vs: sum(vs))
    average = valmap(lambda v: v / sum(average.values()), average)
    average = sorted(average.items(), key=lambda s: order.index(s[0]))
    return average

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

title = Image.from_text("Most representative flag per continent".upper(), calibri(48, bold=True))
label1 = Image.from_text("calculated by combining the colors of all the relevant flags:", calibri(24, italics=True))
label2 = Image.from_text("quantizing them to heraldic colors:", calibri(24, italics=True))
checkers = Checkers((40*len(HeraldicPalette), 40), GradientColormap(*HeraldicPalette), shape=(len(HeraldicPalette), 1), colors=len(HeraldicPalette)).add_grid((len(HeraldicPalette), 1))
label3 = Image.from_text("and then finding the flag with the most similar color composition.", calibri(24, italics=True))

img = Image.from_column([title, label1, allflags, label2, checkers, label3, Rectangle((0,20)), grid], padding=5, bg="white")
img.save("output/flagsaverage4.png")
