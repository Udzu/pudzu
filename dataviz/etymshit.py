import sys
sys.path.append('..')
from charts import *
from bamboo import *
import seaborn as sns

# generate map
df = pd.read_csv("datasets/etymshit.csv").split_columns("group", "|").set_index("language")

CATEGORIES = [
("kakka", 'from Proto-Indo-European *kakka- ("defecate")'),
("strent", 'from Proto-Indo-European *(s)terǵ- ("dirt, dung")'),
("skita", 'from Proto-Germanic *skīta- ("to separate")'),
("merda", 'from Proto-Italic *(s)merdā ("stench")'),
("govьno", 'from Proto-Slavic *govьno ("excrement")'),
("lajьno", 'from Proto-Slavic **lajьno ("flax?")'),
("paska", 'from  Proto-Finno-Ugric *pućka ("excrement?")'),
("suds", 'from Proto-Baltic??'),
("other", "\n".join([
'bok: from Proto-Turkic *bok ("dirt, dung")',
'hara: from Arabic ḵarāʾ ("defecate")',
'lort: from Proto-Germanic *lurtaz ("crooked")',
'mut: from Proto-Indo-European *meu ("moist")',
'rahat: from Turkish rahat ("delight")',
'szar: from Proto-Finno-Urgic *śarɜ ("to dry?")',
'tifa: from Latin pasta ("paste") via pastifarada?'
]))
## ("śarɜ", 'from Proto-Finno-Urgic *śarɜ ("to dry?")'),
## ("hara", 'from Arabic ḵarāʾ ("defecate")'),
## ("rāḥa", 'from Turkish rahat ("delight")'),
## ("mut", 'from Proto-Indo-European *meu ("moist")'),
## ("bok", 'from Proto-Turkic *bok ("dirt, dung")'),
## ("pasta", 'possibly from Latin pasta ("paste")'),
## ('lurtaz', 'from Proto-Germanic *lurtaz ("crooked")'),
]

GROUPS = [n for n,_ in CATEGORIES]
#COLORS = ImageColor.from_floats(sns.cubehelix_palette(15, start=-1.5, rot=1.5, light=0.85, dark=0.15))
COLORS = ImageColor.from_floats(sns.color_palette("Set2", len(CATEGORIES)))
COLORS[-1], COLORS[7] = COLORS[7], COLORS[-1]

def catcol(cat):
    return COLORS[-1] if cat not in GROUPS else COLORS[GROUPS.index(cat)]

def stripes(colors, height=4, width=100):
    return Image.from_column([Image.new("RGBA", (width, height), c) for c in colors])

def colorfn(c):
    if c in ['Sea', 'Language Borders']: return "white"
    elif c in ['Country Borders']: return "#AAAAAA"
    elif c not in df.index: return "grey"
    elif len(df.group[c]) == 1: return catcol(df.group[c][0])
    else: return stripes([catcol(c) for c in df.group[c]])
    
def labelfn(c, w, h):
    if c not in df.index: return None
    fg = "white" if c in ["Lithuanian", "Latvian"] else "black"
    label = df.word[c].replace("\\n", "\n")
    return Image.from_text_bounded(label, (w, h), 24, papply(arial, bold=True), fg=fg, align="center", padding=(0,0,0,3))
    
map = map_chart("maps/Eurolang.png", colorfn, labelfn)

# legend

def box(c, shape=(25,25)): return Image.new("RGBA", shape, c)
def boxtext(s): return Image.from_text(s, arial(14), padding=(10,0,0,3), align="left")
def sectiontext(s): return Image.from_text(s, arial(16, bold=True))

boxes = Image.from_array([[box(COLORS[i],(25,25 if i+1<len(CATEGORIES) else 100)), boxtext(s)] for i,(_,s) in enumerate(CATEGORIES)], bg="white", xalign=0)

section = boxes # Image.from_column([sectiontext("Name origin"), boxes], bg="white", xalign=0, padding=(0,5))

legend = Image.from_column([section], bg="white", xalign=0, padding=10).pad(1, "black")
chart = map.place(legend, align=(1,0), padding=10)

title = Image.from_column([
Image.from_text("A shit by any other name...".upper(), arial(48, bold=True)),
Image.from_text("the etymology of shit in different European languages", arial(36))],
bg="white")

img = Image.from_column([title, chart], bg="white", padding=2)
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/etymshit.png")
