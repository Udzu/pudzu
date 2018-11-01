from pudzu.charts import *
from pudzu.bamboo import *

COLS = ["TOPIC", "WHATSIT", "DOODAH" ]

TFG, TBG = "white", "#00008B"
MFG, MBG = "black", "#F5F5DC"
GFG, GBG = "#F5F5DC", "black"

df = pd.read_csv("datasets/linghybrid.csv")
df.columns = COLS

title = Image.from_text_bounded("Linguistic meme template #7\n— Hybrid words".upper(), 400, 36, papply(arial, bold=True), fg=TFG, bg=TBG, padding=10)
title = title.pad_to_aspect(400, title.height, bg=TBG)

description = Image.from_text_bounded("\n“{} make(s) me sick!”\n\n(pause)\n\n“It should be either {} or {}.\nMixing Latin and Greek roots is wrong!”\n".format(*COLS), 400, 36, papply(arial, bold=True), fg=MFG, bg=MBG, padding=10, line_spacing=10)
description = description.pad_to_aspect(400, description.height, bg=MBG)

grid = grid_chart(df, lambda s: Image.from_text(s, arial(16, bold=True), GFG, GBG), padding=(10,4), col_label=arial(16, bold=True), bg=GBG, fg=GFG).pad((0,0,0,4), GBG)
grid = grid.pad_to_aspect(400, grid.height, bg=GBG)

img = Image.from_column([title, description, grid])
img.save("output/linghybrid.png")