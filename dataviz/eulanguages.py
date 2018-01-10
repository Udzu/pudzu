import sys
sys.path.append('..')
from charts import *
from bamboo import *
import seaborn as sns

df = pd.read_csv("datasets/eulanguages.csv").set_index("country")

# Map 0

cmap = sns.cubehelix_palette(start=.5, rot=-.75, as_cmap=True)

def colorfn0(c):
    if c in ['Sea', 'Borders']: return "white"
    elif c not in df.index: return "#AAAAAA"
    return RGBA(cmap(df.trilingual[c] / 100))

def labelfn0(c, w, h):
    if c not in df.index: return None
    return Image.from_text_bounded("{}%".format(df.trilingual[c]), (w, h), 24, papply(arial, bold=True), fg="black", padding=(0,0,0,2))
    
map0 = map_chart("maps/Europe.png", colorfn0, labelfn0)
gradient0 = Image.from_gradient(cmap, (40, 200), direction=(0,-1)).add_grid((1,5))
legend0 = generate_legend([gradient0], [["{}%".format(i*20) for i in reversed(range(6))]], header="Trilingualism", footer="percentage of the population that can converse in at least 2 foreign languages.", max_width=150)
chart0 = map0.place(legend0, align=(1,0), padding=10)
tchart0 = Image.from_column([Image.from_text("Prevalence of trilingualism".upper(), arial(48, bold=True)), chart0], bg="white", padding=5)

# Map 1

categories = ["English", "French", "Russian", "German", "Spanish"]
othercol = "#808080"

@artial(ignoring_exceptions, othercol)
def catcol(c): return VegaPalette10[categories.index(c.title())]

def colorfn1(c):
    if c in ['Sea', 'Borders']: return "white"
    elif c not in df.index: return "#AAAAAA"
    return Diamond(8, catcol(df.language2[c]), catcol(df.language1[c])).pad(2, catcol(df.language1[c]))
    
map1 = map_chart("maps/Europe.png", colorfn1)
    
others = Image.from_column([Image.from_text("Other", arial(16)),
Image.from_text("\n".join([
"Czech: Slovakian",
"Ireland: Irish",
"Malta: Italian",
"Slovenia: Croatian",
"Slovakia: Czech"
]), arial(10), padding=(0,2))], xalign=0)

legend1 = generate_legend(VegaPalette10[:len(categories)] + [othercol],
                         categories + [others],
                         [(40,40)] * len(categories) + [(40,...)],
                         header="Languages", footer="Background colour shows most spoken foreign language; diamonds show second most.", max_width=150)
chart1 = map1.place(legend1, align=(1,0), padding=10)
tchart1 = Image.from_column([Image.from_text("Most spoken foreign languages".upper(), arial(48, bold=True)), chart1], bg="white", padding=5)

# Map 2

categories2 = [ "holiday", "films", "friends", "internet", "work" ]
descriptions2 = [ "on holiday", "films, TV, etc", "with friends", "on the internet", "at work" ]

def colorfn2(c):
    if c in ['Sea', 'Borders']: return "white"
    elif c not in df.index: return "#aaaaaa"
    return VegaPalette10[categories2.index(df.use[c])]
    
map2 = map_chart("maps/Europe.png", colorfn2)
legend2 = generate_legend(VegaPalette10[:len(categories2)], descriptions2, header="Most common use")
chart2 = map2.place(legend2, align=(1,0), padding=10)
tchart2 = Image.from_column([Image.from_text("Most common foreign language use".upper(), arial(48, bold=True)), chart2], bg="white", padding=5)

# Map 3

categories3 = [ "work", "work abroad", "holiday" ]
descriptions3 = [ "work", "working abroad", "holidays" ]

def colorfn3(c):
    if c in ['Sea', 'Borders']: return "white"
    elif c not in df.index: return "#aaaaaa"
    return VegaPalette10[categories3.index(df.advantage[c])]
    
map3 = map_chart("maps/Europe.png", colorfn3)
legend3 = generate_legend(VegaPalette10[:len(categories3)], descriptions3, header="Main advantage")
chart3 = map3.place(legend3, align=(1,0), padding=10)
tchart3 = Image.from_column([Image.from_text("Biggest perceived language advantage".upper(), arial(48, bold=True)), chart3], bg="white", padding=5)
    
# Put them all together
chart = Image.from_array([[tchart0, tchart1], [tchart2, tchart3]])
img = Image.from_column([Image.from_text("Parlez-Sie English, amigo?".upper(), arial(96, bold=True)),
                         Image.from_text("EU foreign language use according to Special Eurobarometer 386 (2012)", arial(60, italics=True)),
                         chart], padding=10, bg="white")
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img = img.resize_fixed_aspect(scale=0.5)
img.save("output/eulanguages.png")
