from pudzu.charts import *
from pudzu.sandbox.bamboo import *
from PIL import ImageEnhance

df = pd.read_csv("datasets/etymtomato.csv").set_index("language").fillna("t")
FONT = arial
UFONT = partial(font, "fonts/arialu")
LFONT = lambda l: FONT if l not in ["Georgian", "Armenian", "Arabic", "Hebrew", "Persian"] else UFONT

CATEGORIES = ["t", "p", "par", "other"]
PALETTE = [PairedClass12.RED, PairedClass12.ORANGE, PairedClass12.GREEN, PairedClass12.BLUE]

DESCRIPTIONS = [
"""from Proto-Nahuan ***tomatl** ("tomatillo")""",
"""from Italian **pomo d'oro** ("golden apple")""",
"""from German **Paradiesapfel** ("Paradise apple", i.e. the forbidden fruit)
- paradise ult. from Proto-Iranian *paridayjah ("garden")
- Slavic raj ("paradise") ult. from Proto-Iranian *raHíš ("wealth")
- Maltese tadama from tuffieħa ta'Adam ("Adam's apple")
- German Paradeiser used only in Austria""",
"""from another meaning:
- Armenian լոլիկ from *լոլ /lol/ ("round")
- Hebrew עגבניה from עגב ("lust") by influence of German Liebesapfel
- Kazakh qızanaq from qizil ("red")
- Macedonian патлиџан (lit. "aubergine") ult. from Persian بادنجان
- Persian گوجه فرنگی lit. means Western ("Frankish") plum
- Romanian roșie from roșu ("red (aubergine)")"""
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
    label = df.word[c].replace("\\n", "\n").replace("\\u200e","\u200e")
    return Image.from_text_bounded(label, (w, h), 24, papply(LFONT(c), bold=True), align="center", padding=(0,0,0,2))
    
map = map_chart("maps/Eurolang2.png", colorfn, labelfn)
legend = generate_legend(PALETTE[:len(CATEGORIES)], DESCRIPTIONS, box_sizes=(40,...), footer=FOOTER, font_family=partial(FONT, 16))
chart = map.place(legend, align=(1,0))

title = Image.from_column([
Image.from_text("TOMATO IN DIFFERENT LANGUAGES", FONT(48, bold=True)),
Image.from_text("most common terms for tomtato, with etymologies", FONT(36))],
bg="white")

img = Image.from_column([title, chart], bg="white", padding=2)
img = ImageEnhance.Color(img).enhance(0.7)
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/etymtomato.png")

