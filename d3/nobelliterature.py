from pudzu.charts import *
from generate import *


PALETTE = { "n": VegaPalette10.BLUE, "o": VegaPalette10.RED }   

colormap = { i : "o" for i,d in atlas.iterrows() if d.continent in ["South America", "Africa", "Asia"]  and i not in ["Turkey", "Georgia", "Armenia", "Azerbaijan"] }

colormap["Svalbard"] = "#BBBBBB"
colormap["Faroe Islands"] = "#BBBBBB"
colormap["Greenland"] = "#BBBBBB"

colormap["Norway"] = "n"
colormap["Sweden"] = "n"
colormap["Iceland"] = "n"
colormap["Finland"] = "n"
colormap["Denmark"] = "n"


generate_datamap("nobelliterature", colormap, palette=PALETTE)

img = Image.open("temp/nobelliterature.png")
surtitle = Image.from_text("Nobel Literature".upper(), sans(128, bold=True))
title = Image.from_text("The 28 million in blue have produced the same number of\nLiterature Nobel laureates as the 6.5 billion in red (17)".upper(), sans(60, bold=True), align="center")
chart = Image.from_column([title, img], bg="white", padding=10)
chart.place(Image.from_text("/u/Udzu", sans(16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)

chart.save("output/nobelliterature.png")

