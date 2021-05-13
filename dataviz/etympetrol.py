from pudzu.charts import *
from pudzu.sandbox.bamboo import *
from PIL import ImageEnhance

df = pd.read_csv("datasets/etympetrol.csv").set_index("language")
FONT = sans
UFONT = partial(font, "fonts/arialu")
LFONT = lambda l: FONT if l not in ["Georgian", "Armenian", "Arabic", "Hebrew", "Persian"] else UFONT

CATEGORIES = ["b", "p", "g", "e" ]
PALETTE = [PairedClass12.GREEN, PairedClass12.RED, PairedClass12.BLUE, PairedClass12.ORANGE ]

DESCRIPTIONS = [
"""From German **Benzin** < //benzoin// < Arabic //lubān jāwī// (frankinsence of Jawa)
The similarity to German automotive engineer //Karl Benz//'s name is coincidental""",
"""From Medieval Latin **petroleum** (spirits) < //petra// (rock) + //oleum// (oil) < Greek
Originally a UK trade name, but a trademark was denied due to the similarity with the
French (essence de) //pétrole//.""",
"""From **gas** (compound) + **-ol** (< Latin //oleum//) + **-ine** (< Latin //-īnus// as in //gélatine//)
Influenced by UK trademarks **Cazeline** (< John Cassell) and **gazeline** (an Irish copy)""",
"""From **essence** (de pétrole) < Latin //essentia// < //esse// (to be).""",
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
Image.from_text("GASOLINE IN DIFFERENT LANGUAGES", FONT(48, bold=True)),
Image.from_text("most common terms for the motor fuel, with etymologies", FONT(36))],
bg="white")

img = Image.from_column([title, chart], bg="white", padding=2)
img = ImageEnhance.Color(img).enhance(0.7)
img.place(Image.from_text("/u/Udzu", FONT(16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/etympetrol.png")

