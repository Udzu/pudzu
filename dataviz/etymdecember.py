from pudzu.charts import *
from pudzu.experimental.bamboo import *
from PIL import ImageEnhance

df = pd.read_csv("datasets/etymdecember.csv").set_index("language").fillna("December")
FONT = arial
UFONT = partial(font, "fonts/arialu")
LFONT = lambda l: FONT if l not in ["Georgian", "Armenian", "Arabic", "Hebrew", "Persian"] else UFONT

CATEGORIES = ["December", "calque", "Christmas", "dark", "cold", "other"]
PALETTE = [PairedClass12.GREEN, PairedClass12.LIGHTGREEN, PairedClass12.RED, PairedClass12.BLUE, PairedClass12.LIGHTBLUE, PairedClass12.BROWN ]

DESCRIPTIONS = [
"""from Latin **december** (“tenth month”)
   //December was the tenth month in the calendar of Romulus//""",
"""from a **translation** of december:
– Albanian: from //dhjetë// (“ten”)""",
"""from a word referring to **Christmas**:
– Finnish: from //joulu// (“Christmas”) +‎ //kuu// (“month”)
– Basque: from Latin //adventum// (“arrival, Advent")
– Irish: from //Nollaig// (“Christmas”) < Latin //nātālīcia// (“birthday party”)""",
"""from a word referring to **darkness**:
– Czech/Croatian: probably from //prosinoti// (“[sun] shines through”)
– Welsh: from //rhagfyrhau// (“[days] foreshorten”)
– Scottish Gaelic: from //dubh// (“black”)
– Breton: from //kerzu// (“very black”)""",
"""from a word referring to **cold**:
– Belarusian: from //снег// (“snow”)
– Polish etc: from Proto-Slavic //*grudьnъ// (“lump of [frozen] earth”)""",
"""from another meaning:
– Turkish: from //ara// (“gap”),
– Kazakh: from //жел// (“wind”) + //тоқсан// (“quarter”)"""
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
chart = map.place(legend, align=(1,0))

title = Image.from_column([
Image.from_text("DECEMBER IN DIFFERENT LANGUAGES", FONT(48, bold=True)),
Image.from_text("most common terms for December, with etymologies", FONT(36))],
bg="white")

img = Image.from_column([title, chart], bg="white", padding=2)
img = ImageEnhance.Color(img).enhance(0.7)
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/etymdecember.png")

