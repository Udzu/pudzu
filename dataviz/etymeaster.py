from pudzu.charts import *
from pudzu.bamboo import *
import seaborn as sns

# generate map
df = pd.read_csv("datasets/etymeaster.csv").split_columns("group", "|").set_index("language")

CATEGORIES = ["pesach", "great", "easter", "meat", "free", "resurrection", "sacrifice"]
PALETTE = tmap(RGBA, sns.color_palette())
PALETTE = PALETTE[:3] + PALETTE[4:7] + PALETTE[9:]

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
    if c not in df.index: return None
    label = df.word[c].replace("\\n", "\n")
    return Image.from_text_bounded(label, (w, h), 24, papply(font, "fonts/arialu", bold=True), align="center", padding=(0,0,0,2))
    
map = map_chart("maps/Eurolang2.png", colorfn, labelfn)

# legend

def box(c, shape=(45,45)): return Image.new("RGBA", shape, c)
def boxtext(s): return Image.from_text(s, arial(14), padding=(10,0,0,3), max_width=150, align="left")
def sectiontext(s): return Image.from_text(s, arial(16, bold=True))

boxes = Image.from_array([
[box(PALETTE[0]), boxtext("from the Aramaic אחספ meaning Passover, via the Greek Πάσχα.")],
[box(PALETTE[1]), boxtext("from the word for 'great', usually 'great night' or 'great day'.")],
[box(PALETTE[2]), boxtext("from the Germanic goddess Ēostre and her pagan festival.")],
[box(PALETTE[3]), boxtext("from the phrase 'taking meat', referring to the end of Lent.")],
[box(PALETTE[4]), boxtext("from the word for 'free', referring to the end of Lent.")],
[box(PALETTE[5]), boxtext("from the word for 'resurrection'.")],
[box(PALETTE[6]), boxtext("from the word for 'sacrifice'.")]
], bg="white", xalign=0)

section = Image.from_column([sectiontext("Name origin"), boxes], bg="white", xalign=0, padding=(0,5))

legend = Image.from_column([section], bg="white", xalign=0, padding=10).pad(1, "black")
chart = map.place(legend, align=(1,0), padding=10)

title = Image.from_column([
Image.from_text("The different names of Easter".upper(), arial(48, bold=True)),
Image.from_text("etymology of Easter in different European languages", arial(36))],
bg="white")

img = Image.from_column([title, chart], bg="white", padding=2)
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/etymeaster.png")
