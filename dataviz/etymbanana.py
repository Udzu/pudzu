import sys
sys.path.append('..')
from charts import *
from bamboo import *
import seaborn as sns

# generate map
df = pd.read_csv("datasets/etymbanana.csv").split_columns("group", "|").set_index("language")

CATEGORIES = ["p", "b", "m", "o"]
PALETTE = ['#a0b301', '#ffe065','#3a2506', "#cc5555"]
#PALETTE = ['#a0b301', '#ffe065', 

def catcol(cat):
    return PALETTE[CATEGORIES.index(cat)]

def stripes(colors, height=4, width=100):
    return Image.from_column([Image.new("RGBA", (width, height), c) for c in colors])

def colorfn(c):
    if c in ['Sea', 'Language Borders']: return "white"
    elif c in ['Country Borders']: return "#AAAAAA"
    elif c not in df.index: return "grey"
    elif len(df.group[c]) == 1: return catcol(df.group[c][0])
    else: return stripes([catcol(c) for c in df.group[c]])
    
def labelfn(c, w, h):
    fg = "white" if c in ["Turkish"] else "black"
    if c not in df.index: return None
    label = df.word[c].replace("\\n", "\n")
    return Image.from_text_dynamic(label, (w, h), 24, papply(arial, bold=True), fg=fg, align="center", padding=(0,0,0,2))
    
map = map_chart("maps/Eurolang.png", colorfn, labelfn)

# legend

def box(c, shape=(120,80)): return Image.new("RGBA", shape, c)
def boxtext(s): return Image.from_text(s, arial(14), padding=(10,0,0,3), max_width=120, align="left")
def sectiontext(s): return Image.from_text(s, arial(14, bold=True))

boxes = Image.from_array([
[box(PALETTE[0]), boxtext("from the Carib platano")],
[box(PALETTE[1]), boxtext("from the Wolof banana")],
[box(PALETTE[2]), boxtext("from the Arabic mauz")],
[box(PALETTE[3]), boxtext("from the Icelandic for 'sausage fruit' (uncommon)")]
], bg="white", xalign=0)

section = Image.from_column([sectiontext("Word origin"), boxes], bg="white", xalign=0, padding=(0,5))

legend = Image.from_column([section], bg="white", xalign=0, padding=10).pad(1, "black")
chart = map.place(legend, align=(1,0), padding=10)

title = Image.from_column([
Image.from_text("Yes! We Have No Bananas".upper(), arial(48, bold=True)),
Image.from_text("the word banana in different European languages", arial(36))],
bg="white")

img = Image.from_column([title, chart], bg="white", padding=2)
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/etymbanana.png")
