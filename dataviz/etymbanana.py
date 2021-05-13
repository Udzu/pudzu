from pudzu.charts import *
from pudzu.sandbox.bamboo import *
import seaborn as sns

# generate map
df = pd.read_csv("datasets/etymbanana.csv").split_columns("group", "|").set_index("language")

CATEGORIES = ["p", "b", "m", "o"]
PALETTE = ['#a0b301', '#ffe065','#3a2506', "#cc5555"]
#PALETTE = ['#a0b301', '#ffe065', 

FONT = arial
UFONT = partial(font, "fonts/arialu")
LFONT = lambda l: FONT if l not in ["Georgian", "Armenian", "Arabic", "Hebrew", "Persian"] else UFONT

def catcol(cat):
    return PALETTE[CATEGORIES.index(cat)]

def stripes(colors, height=4, width=100):
    return Image.from_column([Image.new("RGBA", (width, height), c) for c in colors])

def colorfn(c):
    if c in ['Sea', 'Language Borders']: return "white"
    elif c in ['Country Borders']: return "#AAAAAA"
    elif c not in df.index: return "grey"
    elif len(df.group[c]) == 1: return catcol(df.group[c][0])
    else: return Stripe(20, *[catcol(c) for c in df.group[c]])
    
def labelfn(c, w, h):
    if c not in df.index: return None
    fg = "white" if df.group[c][0] == "m" else "black"
    label = df.word[c].replace("\\n", "\n")
    return Image.from_text_bounded(label, (w, h), 24, papply(LFONT(c), bold=True), fg=fg, align="center", padding=(0,0,0,2))
    
map = map_chart("maps/Eurolang2.png", colorfn, labelfn)

# legend

DESCRIPTIONS = [
"from the Carib platano", "from the Wolof banana", "from the Arabic mauz", 
"from Icelandic for 'bent fruit'\nor Armenian for 'Adam's fig'" ]

legend = generate_legend(PALETTE, DESCRIPTIONS, header="Word origin", box_sizes=(120,80), box_mask=Image.open("icons/banana.png").convert("L").invert_mask(), font_family=partial(arial, 16))

chart = map.place(legend, align=(1,0), padding=10)

title = Image.from_column([
Image.from_text("Yes! We Have No Bananas".upper(), arial(48, bold=True)),
Image.from_text("the word banana in different European languages", arial(36))],
bg="white")

img = Image.from_column([title, chart], bg="white", padding=2)
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/etymbanana.png")
