from pudzu.charts import *
from generate import *

FONT = sans

PALETTE = {
"j": "#2166ac",
"f": "#92c5de",
"i": "#9970ab",
 }
DESCRIPTIONS = {
"j": "explicitly recognises Jewish community",
"i": """indirectly mentions Jews
- Russia: "Jewish Autonomous Oblast"
- South Africa: "Hebrew for religious purposes"
- Syria: "Zionist enemy\"""",
"f": """formerly mentioned Jews (//incomplete//)
- Ireland: "the Jewish Congregations" (1937-72)
- Norway: "Jews are excluded" (1814-51)""",
}

colormap = {}
for x in ["Egypt", "Iran", "Morocco", "Croatia", "North Macedonia"]: colormap[x] = "j"
for x in ["Ireland", "Norway"]: colormap[x] = "f"
for x in ["South Africa", "Syria", "Russia"] : colormap[x] = "i"

generate_datamap("constituionaljews", colormap, palette=PALETTE, codifier=partial(codify_countries, dependencies=False))

chart = Image.open("temp/constituionaljews.png")
legend = generate_legend(
  [PALETTE[c] for c in DESCRIPTIONS],
  [DESCRIPTIONS.get(c,c) for c in DESCRIPTIONS],
  (40,...), partial(sans, 16), header="Written constitution...".upper())
chart = chart.place(legend, align=(0,1), padding=100)

title = Image.from_column([
Image.from_text("JEWS IN THE CONSTITUTION", sans(72, bold=True)),
Image.from_text("countries with written constitutions that mention Jews or Judaism", sans(36, italics=True))
], bg="white")

img = Image.from_column([title, chart], bg="white", padding=5)
img.place(Image.from_text("/u/Udzu", sans(16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/constituionaljews.png")

