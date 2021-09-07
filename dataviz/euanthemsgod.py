from pudzu.charts import *
from pudzu.sandbox.bamboo import *

df = pd.read_csv("datasets/euanthemsgod.csv").set_index("country")

# generate map
PALETTE = [VegaPalette10.BLUE, VegaPalette10.LIGHTBLUE]
LABELS = [
"current national or royal anthem",
"historic national or royal anthem",
]

FONT = sans

def colorfn(c):
    if c in ['Sea', 'Borders']: return "white"
    if c not in df.index: return "grey"
    if "since" in df.description[c]: return PALETTE[0]
    else: return PALETTE[1]

map = map_chart("maps/Europe.png", colorfn)

legend = generate_legend(PALETTE, LABELS, header="ANTHEM TO THE TUNE OF GOD SAVE THE QUEEN", box_sizes=40, max_width=400, font_family=partial(FONT, 24))

chart = map.place(legend, align=(1,0), padding=10)


listing = Image.from_array([
[Image.from_column(
[
Image.from_url_with_cache(d.flag).to_rgba().resize_fixed_aspect(width=120, height=80).pad(1, "grey"),
Image.from_text(c.upper(), FONT(16, bold=True))
]).pad((0,10), None),

Image.from_column([
Image.from_text('"{}"'.format(d["name"]), FONT(24, bold=True)),
Image.from_text(d.description, FONT(24)),
],xalign=0),
]
for c,d in df.iterrows()], padding=5, xalign=(0.5, 0))


title = Image.from_column([
Image.from_text("God Save the... everyone".upper(), arial(60, bold=True)),
Image.from_text("countries that have had national or royal anthems to the tune of God Save the Queen", arial(28, italics=True)),
], padding=5)

img = Image.from_column([title, chart], bg="white", padding=2)
img = Image.from_row([img, listing], bg="white")

img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/euanthemsgod.png")
