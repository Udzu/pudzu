from functools import partial

from PIL import Image
from pudzu.charts import bar_chart, BarChartLabelPosition
import pandas as pd
from pudzu.pillar import sans, Rectangle

FLAGS = ["https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Flag_of_Israel.svg/1280px-Flag_of_Israel.svg.png",
         "https://upload.wikimedia.org/wikipedia/commons/thumb/0/00/Flag_of_Palestine.svg/1920px-Flag_of_Palestine.svg.png",
         "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/Flag_of_Hamas.svg/1920px-Flag_of_Hamas.svg.png"
         ]
def rlabel(r):
    flag = Image.from_url_with_cache(FLAGS[r]).convert("RGBA").resize((60, 35)).trim(1).pad(1, "grey")
    label = Image.from_text(["Israel", "West Bank", "Gaza"][r], sans(14))
    return Image.from_column([Rectangle((70,0)), flag, label])

def clabel(c,r,v, inside=False):
    if r == 2 and inside or r < 2 and not inside:
        prefix = ["", "", "around "]
        suffix = [" as of 3 March", " as of 15 March", " as of 19 March"]
        source = ["Israel National Council for the Child", "Palestinian Ministry of Health", "Gaza Health Ministry"]
        s = f"{prefix[r]}{v:,}{suffix[r]} [//source: {source[r]}//]"
        return Image.from_markup(s, partial(sans, 16), bg="white" if r < 2 else None, padding=5)

chart = bar_chart(pd.DataFrame([38, 116, 13450], columns=["Deaths"]), 50, 1400,
#          ylabel=Image.from_text("number of children killed", sans(20), padding=15),
          ymax=13500, horizontal=True, label_font=sans(16), label_interval=1000, tick_interval=500, grid_interval=500,
          ylabels=lambda v: f"{v:,}", rlabels=rlabel,
          clabels={BarChartLabelPosition.OUTSIDE: clabel, BarChartLabelPosition.INSIDE: partial(clabel, inside=True)})

title = Image.from_text("Children killed since the October 7 attacks".upper(), sans(36, bold=True))

img = Image.from_column([title, chart, Rectangle((0, 20))], padding=10, bg="white")
img.place(Image.from_text("/u/Udzu", sans(16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/gazachild.png")
