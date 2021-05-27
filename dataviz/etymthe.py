from pudzu.charts import *
from pudzu.sandbox.bamboo import *
from PIL import ImageEnhance

df = pd.read_csv("datasets/etymthe.csv").set_index("language")
df["group"] = df["group"].fillna("n")
df["word"] = df["word"].fillna(" ")
FONT = arial
UFONT = partial(font, "fonts/arialu")
LFONT = lambda l: FONT if l not in ["Georgian", "Armenian", "Arabic", "Hebrew", "Persian"] else UFONT

P = VegaPalette10
PALETTE = [P.ORANGE, P.BLUE, P.GREEN, P.RED, P.PURPLE, P.GREY]
CATEGORIES = ["s", "d", "y", "l", "o", "n"]

DESCRIPTIONS = [
"""from Proto-Celtic //*sindos// (**this**) < ??""",
"""from Proto-Indo-European //*só// (**that**)""",
"""from Proto-Indo-European //*hénos// (**yon**=that there)""",
"""from Latin //illum// (**him/that**) < PIE //*hel-// (**other**)
cognate with the English word //all//""",
"""from another source:
– Arabic/Hebrew possibly from Proto-Semitic //*hal//
– Hungarian from Proto-Uralic //*o// (**that/that other**)
– Macedonian has three definite articles, based on the object's position; one is from //*só//, another from //*hé//""",
"""definite article not used""",
]

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
    
map = map_chart("maps/Eurolang2.png", colorfn, labelfn)
legend = generate_legend(PALETTE[:len(CATEGORIES)], DESCRIPTIONS, box_sizes=(40,...), font_family=partial(FONT, 16), max_width=450)
chart = map.place(legend, align=(1,0))

title = Image.from_column([
Image.from_text("'THE' IN DIFFERENT EUROPEAN LANGUAGES", FONT(48, bold=True)),
],
bg="white")

img = Image.from_column([title, chart], bg="white", padding=2)
img = ImageEnhance.Color(img).enhance(0.7)
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/etymthe.png")

