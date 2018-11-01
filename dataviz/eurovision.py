from pudzu.charts import *
from pudzu.bamboo import *

# generate map
df = pd.read_csv("datasets/eurovision.csv").set_index("country")
PALETTE = ["#fcc900", "#d3d3d3", "#d26c00", VegaPalette10.BLUE, VegaPalette10.PURPLE]
FONT = calibri

def colorfn(c):
    if c in ['Sea']: return 'white'
    elif c in ['Borders']: return "white"
    elif c not in df.index: return "grey"
    pos = ignoring_exceptions(int, 30)(df.position[c])
    if pos <= 3: return PALETTE[pos - 1]
    elif pos <= 10: return PALETTE[3]
    else: return PALETTE[4]
    
def labelfn(c, w,h):
   if c not in df.index: return None
   pos = ignoring_exceptions(int, 30)(df.position[c])
   return first((img for sz in range(20,6,-1) for img in [Image.from_column([
        Image.from_text(str(df.year[c]), FONT(sz, bold=True), max_width=w, align="center"),
        Image.EMPTY_IMAGE if pos <= 3 else Image.from_text("(#{})".format(pos), FONT(sz-2), max_width=w, align="center")
    ])] if img.width <= w and img.height <= h), None)
    
map = map_chart("maps/Europe2.png", colorfn, labelfn)

legend = generate_legend(PALETTE, ["1st", "2nd", "3rd", "4th–10th", "11th+"], header="TOP RANKING", footer="Dates are the\nmost recent\nfor that ranking.", box_sizes=40, max_width=350, fonts=partial(FONT, 16))
chart = map.place(legend, align=(1,0), padding=10)

title = Image.from_column([
Image.from_text("Best Eurovision result by country".upper(), FONT(60, bold=True)),
Image.from_text("not shown: Yugoslavia (1st, 1989), Serbia & Montenegro (2nd, 2004) and Australia (2nd, 2016)", FONT(24, italics=True))],
bg="white", padding=4)
img = Image.from_column([title, chart], bg="white", padding=2)

img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/eurovision.png")
