from pudzu.charts import *
from pudzu.sandbox.bamboo import *
from PIL import ImageEnhance

df = pd.read_csv("datasets/euchristmas.csv").set_index("country")
FONT = sans

PALETTE = {
    "D25": VegaPalette10.BLUE,
    "J7": VegaPalette10.GREEN,
    "J6": VegaPalette10.ORANGE,
    "N": VegaPalette10.RED
}
DESCRIPTIONS = [
    "**25 DECEMBER** (Gregorian & Revised Julian date)",
    "**7 JANUARY** (Old Style Julian date)",
    "**6 JANUARY** (Gregorian Epiphany date)",
    "**NOT A PUBLIC HOLIDAY**",
    "**DATE DEPENDS ON LOCATION**",
    "**TWO PUBLIC HOLIDAYS**",
]
FOOTER = None
 
def colorfn(c):
    if c in ['Sea', 'Borders']: return "white"
    elif c not in df.index: return "grey"
    elif "&" in df.group.get(c):
        colors = [PALETTE[i] for i in df.group[c].split("&")]
        return Stripe(20, *colors)
    elif "|" in df.group.get(c):
        return VegaPalette10.BROWN
    else: return PALETTE[df.group.get(c)]
    
def labelfn(c, w, h):
    if c not in df.index: return None
    label = df.word[c].replace("\\n", "\n")
    return Image.from_text_bounded(label, (w, h), 24, papply(LFONT(c), bold=True), align="center", padding=(0,0,0,2))
    
map = map_chart("maps/Europe2.png", colorfn, None)
boxes = list(PALETTE.values()) + [VegaPalette10.BROWN, Image.from_pattern(Stripe(20, PALETTE["D25"], PALETTE["J7"]), (40,40))]
legend = generate_legend(boxes, DESCRIPTIONS, box_sizes=(40), header="Christmas Day holiday falls on...".upper(), footer=FOOTER, font_family=partial(FONT, 16))
chart = map.place(legend, align=(1,0), padding=50)

title = Image.from_column([
Image.from_text("DATE OF THE CHRISTMAS DAY PUBLIC HOLIDAY", FONT(48, bold=True)),
#Image.from_text("date of Christmas as public holiday", FONT(36))
],
bg="white")

img = Image.from_column([title, chart], bg="white", padding=2)
img = ImageEnhance.Color(img).enhance(0.8)
img.place(Image.from_text("/u/Udzu", FONT(16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/euchristmas.png")

