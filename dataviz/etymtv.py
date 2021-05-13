from pudzu.charts import *
from pudzu.sandbox.bamboo import *

df = pd.read_csv("datasets/etymtv.csv").set_index("language").fillna("tv")

CATEGORIES = ["tv", "tele", "calque", "other"]
DESCRIPTIONS = ["from French **télévision** (coined by Russian scientist Constantin Perskyi), from Greek //τῆλε têle// (far away) + Latin //visum// (vision).",
"from Greek //tele// plus a translation of //vision//.",
"from a translation of both //tele// and //vision//.",
"""from a translation of //vision// but not //tele//:
– Breton //skin// (ray) + //wel// (vision)
– Icelandic //sjón// (vision) + //varp// (projection)"""]
FOOTER = None

PALETTE = [VegaPalette10.BLUE, VegaPalette10.LIGHTBLUE, VegaPalette10.ORANGE, VegaPalette10.RED]
 
FONT = sans
UFONT = partial(font, "fonts/arialu")
LFONT = lambda l: FONT if l not in ["Georgian", "Armenian", "Arabic", "Hebrew", "Persian"] else UFONT

def colorfn(c):
    if c in ['Sea', 'Language Borders']: return "white"
    elif c in ['Country Borders']: return "#AAAAAA"
    elif c not in df.index: return "grey"
    elif "|" in df.group[c]:
        colors = [PALETTE[CATEGORIES.index(i)] for i in df.group[c].split("|")]
        return Stripe(20, *colors)
    else: return PALETTE[CATEGORIES.index(df.group[c])]
    
def labelfn(c, w, h):
    if c not in df.index: return None
    label = df.word[c].replace("\\n", "\n")
    return Image.from_text_bounded(label, (w, h), 24, papply(LFONT(c), bold=True), align="center", padding=(0,0,0,2))
    
map = map_chart("maps/Eurolang2.png", colorfn, labelfn)
legend = generate_legend(PALETTE[:len(DESCRIPTIONS)], DESCRIPTIONS, header="Etymologies", footer=FOOTER, box_sizes=[(40,... if len(d) > 60 else 30) for d in DESCRIPTIONS], max_width=400, font_family=partial(arial, 16))
chart = map.place(legend, align=(1,0), padding=10)
title = Image.from_text("TELEVISION (THE MEDIUM) IN DIFFERENT LANGUAGES", arial(40, bold=True))
img = Image.from_column([title, chart], bg="white", padding=5)
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/etymtv.png")
