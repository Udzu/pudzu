from pudzu.charts import *
from generate import *


PALETTE = { "n": VegaPalette10.BLUE, "o": VegaPalette10.RED }   

colormap = { i : "o" for i,d in atlas.iterrows() if d.continent in ["North America", "Oceania", "South America", "Africa", "Asia"]  and i not in ["French Guiana", "Greenland", "United States of America", "United States", "USA", "US", "Canada"] }

colormap["Norway"] = "n"

generate_datamap("winterolympics", colormap, palette=PALETTE)

img = Image.open("temp/winterolympics.png")
surtitle = Image.from_text("Norway: winter soldiers".upper(), sans(128, bold=True))
title = Image.from_text("The 5 million in blue have won almost twice as many\nWinter Olympic medals (368) as the 6 billion in red (219)".upper(), sans(60, bold=True), align="center")
chart = Image.from_column([title, img], bg="white", padding=10)

chart.save("output/winterolympics.png")

