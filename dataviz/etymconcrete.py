from pudzu.charts import *
from pudzu.sandbox.bamboo import *

df = pd.read_csv("datasets/etymconcrete.csv").set_index("language")

CATEGORIES = ["beton", "concrete", "formigon", "calcestruzzo", "skyrodema", "cruadhtan", "steypa", "karasana"]
DESCRIPTIONS = ["from French **béton**, from Latin //bitumen// (pitch)",
"from English **concrete**, from Latin //concretus// (hardened)",
"possibly from Latin **formicare** (mould), or perhaps from Spanish **hormigo** (cake made of bread crumbs)",
"Italian **calcestruzzo**, from Latin //calcis structio// (limestone structure)",
"Greek **σκυρόδεμα** (gravel-tied)",
"Scottish Gaelic **cruadhtan**, from //cruaidh// (hard)",
"Icelandic **steypa**, from Old Norse //steypa// (mould)",
"Arabic **خرسانة** (???)"]
PALETTE = VegaPalette10
FOOTER = None
 
def colorfn(c):
    if c in ['Sea', 'Language Borders']: return "white"
    elif c in ['Country Borders']: return "#AAAAAA"
    elif c not in df.index: return "grey"
    else: return PALETTE[CATEGORIES.index(df.group.get(c))]
    
def labelfn(c, w, h):
    if c not in df.index: return None
    label = df.word[c].replace("\\n", "\n")
    return Image.from_text_bounded(label, (w, h), 24, papply(font, "fonts/arialu", bold=True), align="center", padding=(0,0,0,2))
    
map = map_chart("maps/Eurolang2.png", colorfn, labelfn)
legend = generate_legend(PALETTE[:len(CATEGORIES)], DESCRIPTIONS, header="Etymologies", footer=FOOTER, box_sizes=[(40,47 if len(d)<90 else 67) for d in DESCRIPTIONS], max_width=320, font_family=partial(font, "fonts/arialu", 16))
chart = map.place(legend, align=(1,0), padding=10)

title = Image.from_column([
Image.from_text("CONCRETE IN DIFFERENT LANGUAGES", arial(48, bold=True)),
Image.from_text("translations and etymologies of the building material", arial(36))],
bg="white")

img = Image.from_column([title, chart], bg="white", padding=2)
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/etymconcrete.png")
