import sys
sys.path.append('..')
from charts import *

PALETTE = { "D": VegaPalette10.BLUE, "R": VegaPalette10.RED, "DR": VegaPalette10.GREEN, "U": VegaPalette10.GREY }
PARTIES = { "D": "Democratic", "R": "Republican", "DR": "Democratic-Republican", "U": "Unaffiliated" }

WIDTH = 220
THUMB_H = 180
NAME_H = 30
LABEL_H = 50
HEIGHT = THUMB_H + NAME_H + LABEL_H
FONT = arial

FONT_SIZE = 24
SMALL_FONT_SIZE = 18
BIG_FONT_SIZE = 32

def code(p,g): return f"{p}p" * bool(p) + f"{g}g" * bool(g)
def category(p,g): return " & \n".join(f"{n} foreign {c}{'s'*(n>1)}" for n,c in ((p,"parent"),(g,"grandparent")) if n)

df = pd.read_csv("datasets/uspresident_ancestry.csv")
pgs = ((2,0),(1,2),(1,1),(1,0),(0,4),(0,3),(0,2),(0,1))
pgs = [(p,g) for p,g in pgs if len(df[df.foreign == code(p,g)])]
data = pd.DataFrame(((len(df[df.foreign == code(p,g)])) for p,g in pgs), index=(category(p,g) for p,g in pgs))

def clabel(c,r,v,w,h):
    boxes = []
    for _, d in df[df.foreign == code(*pgs[r])].iterrows():
        name = Rectangle((WIDTH, LABEL_H), PALETTE[d.party]).place(Image.from_text(d.president, FONT(FONT_SIZE), "white"), align=(0.5,0.6))
        thumb = Image.from_url_with_cache(d.img).to_rgba().cropped_resize((WIDTH, THUMB_H), align=(0.5,0.2))
        label = Rectangle((WIDTH, LABEL_H), PALETTE[d.party]).place(Image.from_text(d.notes.replace(" & ","\n"), FONT(SMALL_FONT_SIZE), "white"), align=(0.5,0))
        boxes.append(Image.from_column([name, thumb, label]))
    return Image.from_row(boxes) if boxes else None

chart = bar_chart(data, HEIGHT, WIDTH*data.max()[0], horizontal=True,
    grid_interval=1, label_interval=1, label_font=FONT(BIG_FONT_SIZE, italics=True),
    clabels={ BarChartLabelPosition.INSIDE : clabel }
    )

title = Image.from_column([
Image.from_text("America's foreignest Presidents".upper(), FONT(64, bold=True), padding=(5,10,5,2)),
Image.from_text("US presidents with foreign-born parents or grandparents", FONT(40, bold=False), padding=(5,2,5,10))
], bg="white")

footer = Image.from_text("*Jefferson's mother's father and Reagan's Canadian grandmother's mother were both American-born. However, inheriting US citizenship through just one parent only became possible in 1855 for fathers and 1934 for mothers.", FONT(FONT_SIZE), max_width = round(chart.width*1.1), padding=10)

img = Image.from_column([title, chart.pad(10, "white"), footer], bg="white")
img.save("output/politics_usforeign.png")
