import sys
sys.path.append('..')
from charts import *
from bamboo import *

df = pd.read_csv("datasets/etymphonemes.csv").set_index("language").fillna("")
FONT = calibri

def combo(c1, c2): return Stripe(10, c1, c2)

def colorfn(c, *args, mapping):
    if c in ['Sea', 'Language Borders']: return "white"
    elif c in ['Country Borders']: return "#AAAAAA"
    cols = [v for k,v in mapping.items() if k in get_non(df.phonemes, c, "")]
    if len(cols) == 0: return "grey"
    elif len(cols) == 1: return cols[0]
    else: return combo(*cols)

def boxfn(pattern, number):
    return Rectangle(40, pattern).place(Image.from_text(str(number), FONT(20, bold=True), "white"))
    
def counts(a, b):
    return [len([x for x in df.phonemes if a not in x and b not in x]),
            len([x for x in df.phonemes if a in x and b not in x]),
            len([x for x in df.phonemes if a not in x and b in x]),
            len([x for x in df.phonemes if a in x and b in x])]
            
def chartfn(pal, descriptions):
    title = Image.from_text("[{}] and [{}]".format(pal[0][0], pal[1][0]), FONT(60, bold=True), "black", padding=10)
    chart = map_chart("maps/Eurolang.png", partial(colorfn, mapping=dict(pal)))
    legend = generate_legend(tmap(boxfn, ["grey", pal[0][1], pal[1][1], combo(pal[0][1], pal[1][1])],
                                         counts(pal[0][0], pal[1][0])), descriptions, header="Distribution", fonts=partial(FONT, 32))
    chart = chart.place(legend, align=(1,0), padding=10)
    return Image.from_column([chart, title], bg="white")

map1 = chartfn([("h", VegaPalette10.BLUE), ("x", VegaPalette10.RED)], ["Neither!", "[h] or [ɦ] as in //hurrah//!", "[x] as in //och//!", "Both!"])
map2 = chartfn([("θ", VegaPalette10.LIGHTGREEN), ("ð", VegaPalette10.GREEN)], ["Neiver of 'em", "[θ] as in //think//", "[ð] as in //this//", "Both of them"])
map3 = chartfn([("ř", VegaPalette10.PINK), ("ɧ", VegaPalette10.ORANGE)], ["No thank you!", "[ř] as in //příklad//", "[ɧ] as in //sju//", "You're kidding, right?"])
chart = Image.from_row([map1, map2, map3])

title = Image.from_text("Distribution of selected consonants in European languages".upper(), FONT(96, bold=True))
img = Image.from_column([title, chart], bg="white", padding=10)
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/etymphonemes.png")
