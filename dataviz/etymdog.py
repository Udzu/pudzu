from pudzu.charts import *
from pudzu.sandbox.bamboo import *
from PIL import ImageEnhance

df = pd.read_csv("datasets/etymdog.csv").set_index("language").fillna("?")
FONT = sans
UFONT = font_family("arial", "/usr/share/fonts/truetype/msttcorefonts/arial")
LFONT = lambda l: FONT if l not in ["Arabic", "Hebrew", "Persian"] else UFONT

CATEGORIES = ["h", "c", "pie", "p", "it", "k", "other", "?" ]
PALETTE = [VegaPalette10.BLUE, VegaPalette10.LIGHTBLUE.blend(VegaPalette10.BLUE, 0.4), VegaPalette10.LIGHTBLUE.brighten(0.1), VegaPalette10.ORANGE, VegaPalette10.BROWN, VegaPalette10.GREEN, VegaPalette10.GREY.brighten(0.1) ]

DESCRIPTIONS = [
"""from Proto-Germanic //*hundaz//, from PIE *kwo ("dog")""",
"""from Latin //canis//, from PIE *kwo ("dog")""",
"""from PIE *kwo ("dog") via other routes:
- Proto-Iranian //*cwā́ // (to Russian via Middle Iranian)
- Proto-Balto-Slavic //*ś(w)ō//
- Proto-Celtic //*kū//""",
"""from Proto-Slavic //*pьsъ// ("dog"), of uncertain origin""",
"""from Proto-Turkic //*it// ("dog") and/or //*köpek// ("dog, herd?")""",
"""from Proto-Semitic //*kalb// ("dog")""",
"""from another source:
- dog: from Old English //dogga//, of uncertain origin
- perro: of uncertain origin
- σκύλος: from Ancient Greek //σκύλαξ// ("puppy"), of uncertain origin
- koira, koer: from Proto-Uralic //*kojera// ("male animal)
- madra: from Proto-Celtic //*maddo// ("dog")
- dzagli: from Proto-Georgian //*z1agl// ("dog", lit. "stupid animal?")
- txakur: from Proto-Basque //*zacuŕ// ("dog")
- gos, kuyta/куче: onomatopoeic""",
]
FOOTER = None
 
def colorfn(c):
    if c in ['Sea', 'Language Borders']: return "white"
    elif c in ['Country Borders']: return "#AAAAAA"
    elif c not in df.index: return "grey"
    elif "|" in df.group.get(c):
        colors = [PALETTE[CATEGORIES.index(i)] for i in df.group[c].split("|")]
        return Stripe(20, *colors)
    else: return PALETTE[CATEGORIES.index(df.group.get(c))]
    
def labelfn(c, w, h):
    if c not in df.index: return None
    label = df.word[c].replace("\\n", "\n")
    return Image.from_text_bounded(label, (w, h), 24, papply(LFONT(c), bold=True), align="center", padding=(0,0,0,2))
    
map = map_chart("maps/Eurolang2.png", colorfn, labelfn)
legend = generate_legend(PALETTE[:len(CATEGORIES)], DESCRIPTIONS, box_sizes=(40,...), footer=FOOTER, font_family=partial(FONT, 16))
chart = map.place(legend, align=(1,0), padding=10)

title = Image.from_column([
Image.from_text("THE WORD FOR 'DOG' IN DIFFERENT LANGUAGES", FONT(48, bold=True)),
#Image.from_text("most common terms for the motor fuel, with etymologies", FONT(36)),
],
bg="white")

img = Image.from_column([title, chart], bg="white", padding=2)
img = ImageEnhance.Color(img).enhance(0.7)
img.place(Image.from_text("/u/Udzu", FONT(16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/etymdog.png")

