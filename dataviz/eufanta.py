from pudzu.pillar import *
from pudzu.charts import *

# generate map
df = pd.read_csv("datasets/fanta.csv").set_index("country")

FONT = sans
CUTOFFS = [20, 12, 8, 5.4, 5, 4, 3, 0]
LABELS = ["20%", "12%", "8%", "6%", "5% or 5.3%", "4.5%", "3%"]
PALETTE = """#ffffe5
#fff7bc
#fee391
#fec44f
#fe9929
#ec7014
#cc4c02
#993404
#662506""".split()[::-1][:-2]



def colorfn(c):
    if c in ['Sea', 'Borders']:
        return "white"
    elif c not in df.index:
        return print(c) or "grey"
    return PALETTE[next(i for i, x in enumerate(CUTOFFS) if float(df.pc[c].rstrip("*")) >= x)]


def labelfn(c, w, h):
    if c not in df.index: return None
    label = df.pc[c] + "%"
    if "*" in label: label = label.replace("*", "") + "*"
    pc = float(df.pc[c].rstrip("*"))
    return Image.from_text(label, FONT(20), "black" if pc < 12 else "white")

map = map_chart("maps/Europe.png", colorfn, labelfn)

HEADER = "Juice content:"
FOOTER = "* including some\nnon-orange citric juice"
legend = generate_legend(PALETTE, LABELS, box_sizes=40,
                         header=HEADER, footer=FOOTER, font_family=partial(FONT, 24))
chart = map.place(legend, align=(1, 0), padding=(40,60))

title = Image.from_column([
    Image.from_text("JUICE CONTENT OF FANTA ORANGE", FONT(48, bold=True)),
    Image.from_markup("Sourced from [[https:\//www.coca-cola.com]]. US Fanta Orange contains no juice.", partial(FONT, 24))],
    padding=4,
    bg="white")

img = Image.from_column([title, chart], bg="white", padding=2)
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black",padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/eufanta.png")
