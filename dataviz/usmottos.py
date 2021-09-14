from pudzu.charts import *
from pudzu.sandbox.bamboo import *

df = pd.read_csv("datasets/usmottos.csv").fillna("").set_index("state")

# generate map
PALETTE = [VegaPalette10.RED, VegaPalette10.BLUE, VegaPalette10.LIGHTBLUE, VegaPalette10.ORANGE, VegaPalette10.GREEN, VegaPalette10.LIGHTGREEN]
LABELS = [
"**English**",
"**Latin**",
"""**Romance language**
– French (Minnesota)
– Italian (Maryland)
– Spanish (Montana)""",
"**Greek** (and English)",
"**Hawaiian**",
"**Chinook Jargon**",
]
PALETTE = PALETTE[:len(LABELS)]

FONT = sans

translated = True

def colorfn(c):
    if c in ['Sea', 'Borders']: return "white"
    cs = []
    for language in df.language[c].split("|"):
        if language == "English": cs.append(PALETTE[0])
        if language == "Latin": cs.append(PALETTE[1])
        if language in ("Spanish", "French", "Italian"): cs.append(PALETTE[2])
        if language == "Greek": cs.append(PALETTE[3])
        if language == "Hawaiian": cs.append(PALETTE[4])
        if language == "Chinook": cs.append(PALETTE[5])
    if len(cs) == 0: return "grey"
    if len(cs) == 1: return cs[0]
    if len(cs) == 2: return Stripe(20, *cs)
    
def labelfn(c, w,h):
    if c not in df.index: return None
    motto = df.english[c].upper() if translated else df.motto[c].upper()
    return Image.from_text_bounded(motto.replace("|"," / "), (w, h), 24, partial(FONT, bold=True, italics=False and df.language[c] != "English"), max_width=w, soft_max_width=True, align="center")
   
map = map_chart("maps/USA.png", colorfn, labelfn)

ORDER = [0,3,1,2,4,5]
PALETTE = [PALETTE[x] for x in ORDER]
LABELS = [LABELS[x] for x in ORDER]

legend = generate_legend(PALETTE, LABELS, header="STATE MOTTO LANGUAGE", footer="Kentucky, North Dakota, South Carolina and Vermont also have an additional Latin motto.", max_width=250, box_sizes=(40,...), font_family=partial(FONT, 18))

chart = map.place(legend, align=(1,0.95), padding=10)

title = Image.from_text(f"{'Translations' if translated else 'Languages'} of the US state mottos".upper(), arial(60, bold=True), padding=10)

img = Image.from_column([title, chart], bg="white", padding=2)
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/usmottos.png")
