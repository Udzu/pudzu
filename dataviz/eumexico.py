from pudzu.charts import *
from pudzu.sandbox.bamboo import *
import seaborn as sns


s = { "Italy", "Malta" }
sh = { "Portugal" }
x = { "Spain", "Estonia", "Slovenia" }

PALETTE = { "s": VegaPalette10.LIGHTBLUE, "sh": VegaPalette10.ORANGE, "x": VegaPalette10.RED, "ks" : VegaPalette10.BLUE }

def colorfn(c):
    if c in x:
        return PALETTE["x"]
    elif c in s:
        return PALETTE["s"]
    elif c in sh:
        return PALETTE["sh"]
    elif c in ["Sea", "Borders"]:
        return "white"
    else:
        return PALETTE["ks"]


map = map_chart("maps/Europe2.png", colorfn)
legend = generate_legend(
  [PALETTE["x"], PALETTE["sh"], PALETTE["s"], PALETTE["ks"]],
  ["kh or h — current endonym",
   "sh — original Nahuatl pronunciation",
   "ss — cluster reduction",
   "ks (or kz) — spelling pronunciation",
   ], 60, partial(arial, 24), header="the X in Mexico is pronounced".upper(), max_width=600)

chart = map.place(legend, align=(1,0), padding=10)

# title
title = Image.from_column([
Image.from_text("ME?IKO", arial(180, bold=True)),
Image.from_text("the most common pronunciation of the X in Mexico",
                arial(36, italics=True),
                max_width=1400, align="center", padding=8),
],
bg="white")

img = Image.from_column([title, chart], bg="white", padding=2)
img.place(Image.from_text("/u/Udzu", arial(16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)

img.save(f"output/eumexico.png")

