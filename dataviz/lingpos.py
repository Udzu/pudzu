from pudzu.charts import *
from pudzu.bamboo import *

COLS = ["WORDCLASS", "EXAMPLE1", "EXAMPLE2" ]

TFG, TBG = "white", "#00008B"
MFG, MBG = "black", "#F5F5DC"
GFG, GBG = "#F5F5DC", "black"

df = pd.read_csv("datasets/lingpos.csv")
df.columns = COLS

title = Image.from_text_bounded("Linguistic meme template #3\n— Parts of speech".upper(), 400, 36, papply(arial, bold=True), fg=TFG, bg=TBG, padding=10)
title = title.pad_to_aspect(400, title.height, bg=TBG)

description = Image.from_text_bounded("\n“I really like {}!”\n\n“You know, like {} or {}.”\n".format(*COLS), 400, 36, papply(arial, bold=True), fg=MFG, bg=MBG, padding=10, line_spacing=10)
description = description.pad_to_aspect(400, description.height, bg=MBG)

grid = grid_chart(df, lambda s: Image.from_text(s, arial(12 if "enough" in s else 16, bold=True, italics="enough" in s), GFG, GBG, padding=(0,2*int("enough" in s),0,0)), padding=(10,4), col_label=arial(16, bold=True), bg=GBG, fg=GFG).pad((0,0,0,4), GBG)
grid = grid.pad_to_aspect(400, grid.height, bg=GBG)

img = Image.from_column([title, description, grid])
img.save("output/lingpos.png")