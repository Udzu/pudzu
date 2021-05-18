from pudzu.charts import *
from pudzu.sandbox.bamboo import *
from PIL import ImageEnhance

df = pd.read_csv("datasets/etymno.csv").set_index("language")
df["group"] = df["group"].fillna("v")
df["word"] = df["word"].fillna(" ")
FONT = sans # arial
UFONT = sans # partial(font, "fonts/arialu")
LFONT = lambda l: FONT if l not in ["Georgian", "Armenian", "Arabic", "Hebrew", "Persian"] else UFONT

PALETTE = [VegaPalette10[x] for x in "BLUE, LIGHTBLUE, ORANGE, GREEN, RED, PURPLE, BROWN, PINK".split(", ")]
CATEGORIES = ["n", "c", "f", "o", "e", "l", "t"]

DESCRIPTIONS = [
"""from the Proto-Indo-European //*ne// ("not")""",
"""normally the negated form of the verb is used instead of 'no', but where a standalone form is used it typically derives from //*ne//""",
"""from Proto-Finno-Ugric //*ne// ("not") or //*e-// (negative verb stem)""",
"""possibly from Proto-Indo-European *(ne) h₂óyu kʷid ("(not) on your life")""",
"""from Proto-Basque *eze ("not")""",
"""from Proto-Semitic //*lā// ("not")""",
"""from Proto-Turkic //*yōk// ("no")
from clipping of Persian //na xeyr// < no + Arabic //khayr// good""",
]

FOOTER = "Irish and Scottish Gaelic"
 
def colorfn(c):
    cols = ValueBox()
    if c in ['Sea', 'Language Borders']: return "white"
    elif c in ['Country Borders']: return "#AAAAAA"
    elif c not in df.index: return "grey"
    elif (df.word.get(c) == " "): return "grey"
    elif len(cols << [PALETTE[CATEGORIES.index(x)] for x in df.group.get(c)]) == 1: return cols()[0]
    else: return Stripe(20, cols()[0], cols()[1])
    
def labelfn(c, w, h):
    if c not in df.index: return None
    label = df.word[c].replace("\\n", "\n")
    return Image.from_text_bounded(label, (w, h), 24, papply(LFONT(c), bold=True), align="center", padding=(0,0,0,2))
    
map = map_chart("maps/Eurolang.png", colorfn, labelfn)
legend = generate_legend(PALETTE[:len(CATEGORIES)], DESCRIPTIONS, box_sizes=(40,...), footer=FOOTER, font_family=partial(FONT, 16), max_width=400)
chart = map.place(legend, align=(1,0))

title = Image.from_column([
Image.from_text("NO IN DIFFERENT EUROPEAN LANGUAGES", FONT(48, bold=True)),
],
bg="white")

img = Image.from_column([title, chart], bg="white", padding=2)
img = ImageEnhance.Color(img).enhance(0.7)
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/etymno.png")

