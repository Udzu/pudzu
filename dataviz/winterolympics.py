import sys

sys.path.append('..')
from charts import *
from bamboo import *

data = [
("Norway", "5m", 118, 111, 100),
("USA", "323m", 96, 102, 84),
("China, Japan and countries beginning with K", "1684m", 49, 60, 51),
("rest of Asia, Africa and\nLatin America", "4643m", 0, 0, 1)
]
table = pd.DataFrame(data, columns=["name", "population", "gold", "silver", "bronze"]).set_index("name")

PALETTE = ["#fcc900", "#d3d3d3", "#d26c00"]

def rlabel(r):
    return Image.from_column([
        Image.from_text(table.index[r], arial(14), align="center", max_width=105, padding=(0,2,0,3)),
        Image.from_text("(pop. {})".format(table.population[r]), arial(14, italics=True), align="center", max_width=105, padding=(0,2))
        ], bg="white")
    
def clabel(c, r, v):
    return Image.EMPTY_IMAGE if v < 10 and c >= 0 else Image.from_text(str(v), arial(14))
 
ylabel = Image.from_text("# Winter Olympics medals won", arial(16), padding=(5,2,5,10), bg="white").transpose(Image.ROTATE_90)

chart = bar_chart(table[["gold", "silver", "bronze"]], 90, 600, type=BarChartType.STACKED, colors=PALETTE, spacing=10,
    grid_interval=50, tick_interval=25, ylabels=arial(16), ymax=350, ylabel=ylabel,
    rlabels=rlabel, clabels=clabel)

legend = Image.from_column([
Image.from_text("compared regions", arial(16, bold=True)),
Image.EMPTY_IMAGE.pad((0,5)),
Image.open("cache/winterolympics_map.png").resize_fixed_aspect(width=250),
Image.EMPTY_IMAGE.pad((0,10)),
Image.from_text("a new flag?", arial(16, bold=True)),
Image.EMPTY_IMAGE.pad((0,5)),
Image.from_text("since the current Winter Olympics flag represents the five inhabited continents of the world", arial(16), max_width=250),
Image.open("cache/winterolympics_flag.png").resize_fixed_aspect(width=250),
Image.from_text("a more accurate flag might be:", arial(16)),
Image.open("cache/winterolympics_flag2.png").resize_fixed_aspect(width=250)], xalign=0, bg="white").pad(5,"white").pad(1,"black")

img = Image.from_row([
chart,
legend.pad(10, "white")
], bg="white", yalign=0)
img = img.pin(clabel(-1, -1, 1), (360 + 110, 596))

img = Image.from_column([
Image.from_text("Winter Olympics medals".upper(), arial(40, bold=True), padding=(0,10,0,2)),
Image.from_text("geographic distribution across selected regions", arial(24, bold=False), padding=(0,2,0,10)),
img], bg="white").pad((0,0,0,2), "white")

img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/politics_winterolympics.png")
