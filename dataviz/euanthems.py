from pudzu.charts import *
from pudzu.sandbox.bamboo import *

minor = """Bulgaria
Azerbaijan
Kazakhstan
Israel
Iraq
Romania
Slovakia
Turkey""".split("\n")

wordless = """Spain
Bosnia
San Marino
Kosovo""".split("\n")

unknown = """UK
Slovakia
Poland
Sweden
Liechtenstein""".split("\n")

names = {
"UK": "God Save\nthe Queen",
"Spain": "La Marcha Real",
"Poland": "Mazurek\nDąbrowskiego",
"Slovakia": "Nad Tatrou\nsa blýska",
"Romania": "Desteaptă-te,\nromâne!",
"Azerbaijan": "Azərbaycan\nmarşı",
"Kazakhstan": "Meniñ\nQazaqstanım",
"Turkey": "İstiklâl Marşı",
"Bosnia": "Državna himna\nBosne i\nHercegovine",
"Kosovo": "Europe",
"Bulgaria": "Mila Rodino",
"Sweden": " Du gamla, \ndu fria",
"Finland": "Maamme",
"Estonia": "Mu isamaa,\nmu õnn\nja rõõm",
"Greece": "Ýmnos eis\ntīn Eleutherían",
}

same = """UK
Liechtenstein
Greece
Cyprus
Estonia
Finland""".split("\n")

# EStonia-Finland, UK-Liechtenstein, Greece-Cyprus

# generate map
PALETTE = [VegaPalette10.BLUE, VegaPalette10.ORANGE, VegaPalette10.RED, VegaPalette10.PURPLE]
LABELS = [
"a minor key",
"no official lyrics",
"unknown melody composer",
"same melody as another modern anthem",
]

FONT = sans

#PALETTE.insert(1, Rectangle(40, Stripe(20, PALETTE[0], PALETTE[1])))


def colorfn(c):
    if c in ['Sea', 'Borders']: return "white"
    cs = []
    if c in ["Israel", "Iraq"]: return PALETTE[0].blend("#C0C0C0", 0.6)
    if c in minor: cs.append(PALETTE[0])
    if c in wordless: cs.append(PALETTE[1])
    if c in unknown: cs.append(PALETTE[2])
    if c in same: cs.append(PALETTE[3])
    if c in ["Iraq", "Jordan", "Saudi Arabia", "Iran", "Morocco", "Syria", "Lebanon", "Palestine", "Tunisia", "Algeria"]: return "#C0C0C0"
    if not cs: return "#808080"
    if len(cs) == 1: return cs[0]
    if len(cs) == 2: return Rectangle(40, Stripe(20, *cs))
    
def labelfn(c, w,h):
   if c not in names: return None
   return Image.from_text_bounded(names[c], (w, h), 24, papply(FONT, bold=True), "white", align="center", padding=2).add_shadow("black", blur=2, resize=False)

map = map_chart("maps/Europe2.png", colorfn, labelfn)

ORDER = [3, 0, 1, 2]
PALETTE = [PALETTE[x] for x in ORDER]
LABELS = [LABELS[x] for x in ORDER]
legend = generate_legend(PALETTE, LABELS, header="NATIONAL ANTHEM WITH", box_sizes=40, font_family=partial(FONT, 24))

chart = map.place(legend, align=(1,0), padding=10)

title = Image.from_text("Some Unusual European national anthems".upper(), arial(48, bold=True), padding=10)

img = Image.from_column([title, chart], bg="white", padding=2)
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/euanthems.png")
