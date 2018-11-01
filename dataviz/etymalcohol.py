from pudzu.charts import *
from pudzu.bamboo import *

df = pd.read_csv("datasets/etymalcohol.csv").set_index("language")

CATEGORIES = ["a", "iconcrete", "formigon", "calcestruzzo", "skyrodema", "cruadhtan", "steypa"]
DESCRIPTIONS = ["from European alchemical jargon, ultimately from Arabic اَلْكُحُول //al-kuḥūl// (the kohl, a powder used as eye cosmetic).",
"from Icelandic //áfengur// (intoxicating), somehow connected to the preposition //á// (on) and verb //fá// (receive)."]

PALETTE = VegaPalette10
FOOTER = None
 
def colorfn(c):
    if c in ['Sea', 'Language Borders']: return "white"
    elif c in ['Country Borders']: return "#AAAAAA"
    elif c not in df.index: return "grey"
    else: return PALETTE[df.word[c] == "áfengi"]
    
def labelfn(c, w, h):
    if c not in df.index: return None
    label = df.word[c].replace("\\n", "\n")
    return Image.from_text_bounded(label, (w, h), 24, papply(arial, bold=True), align="center", padding=(0,0,0,2))
    
map = map_chart("maps/Eurolang.png", colorfn, labelfn)
legend = generate_legend(PALETTE[:len(DESCRIPTIONS)], DESCRIPTIONS, header="Etymologies", footer=FOOTER, box_sizes=[(120,...) for d in DESCRIPTIONS], max_width=400, fonts=partial(arial, 16))
chart = map.place(legend, align=(1,0), padding=10)

title = Image.from_column([
Image.from_text("ALCOHOL IN DIFFERENT LANGUAGES", arial(48, bold=True)),
Image.from_markup("//(a.k.a. linguistic purism in Icelandic)//", partial(arial, 40))],
bg="white")

img = Image.from_column([title, chart], bg="white", padding=5)
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/etymalcohol.png")
