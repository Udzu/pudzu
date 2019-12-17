from pudzu.charts import *
from pudzu.experimental.bamboo import *
from PIL import ImageEnhance

df = pd.read_csv("datasets/etymeighty.csv").set_index("language")
FONT = arial
UFONT = partial(font, "fonts/arialu")
LFONT = lambda l: FONT if l not in ["Georgian", "Armenian", "Arabic", "Hebrew", "Persian"] else UFONT

PALETTE = [PairedClass12.RED, PairedClass12.PINK, PairedClass12.BLUE, PairedClass12.LIGHTBLUE, PairedClass12.GREEN ]
CATEGORIES = ["8", "e", "4"]

DESCRIPTIONS = [
"""a combination of **eight** and **ten**:
– from Latin: //octōgintā// < PIE //*oktōḱomt//
– from Proto-Germanic: //*ahtōu// + //*-tigaz//
– from Proto-Slavic: //*osmь// + //*desętь//
– from Proto-Balto-Slavic: //*aḱtō-// + //*deśimt//
– from Proto-Finnic: //*kakteksa// (literally "two-from-ten") + //*kümmen//
– from Proto-Turkic: //*sekiz// + //*ōn//
– Hungarian is from //nyolc// << Proto-Ugric //*ńalɜ// + //van// << Turkic //on//
– Irish is a clipping of //ochtmoga//
– English was previously //hundeahtatig// ("decade-eight-tens")
– some Swiss French dialects use //huitante//""",
"""from **eight** only:
– from Proto-Semitic //*ṯamāniy//""",
"""a combination of **four** and **twenty**
– from Proto-Celtic: //*kʷetwares// + //*wikantī//
– from Proto-Kartvelian: //*otxo// + //*oci//
– Danish is a clipping of //firsindstyve// ("four-times-twenty")
– Irish scór is borrowed from English.
– French use of vigesimal is derived from Gaulish
– Albanian previously used //katërzetë//""",
]
FOOTER = """Irish, Welsh, Scottish Gaelic have two counting systems: a traditional
vigesimal one and a new decimal one."""
 
def colorfn(c):
    cols = ValueBox()
    if c in ['Sea', 'Language Borders']: return "white"
    elif c in ['Country Borders']: return "#AAAAAA"
    elif c not in df.index: return "grey"
    elif len(cols << [PALETTE[CATEGORIES.index(x)] for x in df.group.get(c)]) == 1: return cols()[0]
    else: return Stripe(10, cols()[0], cols()[1])
    
def labelfn(c, w, h):
    if c not in df.index: return None
    label = df.word[c].replace("\\n", "\n")
    return Image.from_text_bounded(label, (w, h), 24, papply(LFONT(c), bold=True), align="center", padding=(0,0,0,2))
    
map = map_chart("maps/Eurolang2.png", colorfn, labelfn)
legend = generate_legend(PALETTE[:len(CATEGORIES)], DESCRIPTIONS, box_sizes=(40,...), footer=FOOTER, fonts=partial(FONT, 16))
chart = map.place(legend, align=(1,0))

title = Image.from_column([
Image.from_text("EIGHTY IN DIFFERENT EUROPEAN LANGUAGES", FONT(48, bold=True)),
Image.from_text("decimal versus vigesimal counting systems", FONT(36))],
bg="white")

img = Image.from_column([title, chart], bg="white", padding=2)
img = ImageEnhance.Color(img).enhance(0.7)
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/etymeighty.png")

