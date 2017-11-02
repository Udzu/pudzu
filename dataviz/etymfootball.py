import sys
sys.path.append('..')
from charts import *
from bamboo import *
import seaborn as sns

# generate map
df = pd.read_csv("datasets/etymfootball.csv").split_columns("group", "|").set_index("language")

CATEGORIES = ["origin", "loan", "germanic", "calque", "soccer", "kick", "leg"]
PALETTE = ['#28455a', '#3c7f6b', '#79aa73', '#c7c79e', "#844f96", "#cc5555", "#e7de80"]
#PALETTE = ["#1764ab", "#4a97c9", "#326e69", "#70a771", "#844f96", "#cc5555", "#ccb974"]

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
    return Image.from_text_bounded(label, (w, h), 24, papply(arial, bold=True), align="center", padding=(0,0,0,2))
    
map = map_chart("maps/Eurolang.png", colorfn, labelfn)

# legend

def box(c, box_size=40): return Image.new("RGBA", (box_size, box_size), c)
def boxtext(s): return Image.from_text(s, arial(14), padding=(10,0,0,3), max_width=150, align="left")
def sectiontext(s): return Image.from_text(s, arial(14, bold=True))

football_boxes = Image.from_array([
[box(PALETTE[0]), boxtext("Football")],
[box(PALETTE[1]), boxtext("Direct loan")],
[box(PALETTE[2]), boxtext("Translation to a Germanic language")],
[box(PALETTE[3]), boxtext("Translation to other languages")],
[box(PALETTE[6]), boxtext("Translation with 'foot' but not 'ball'")]
], bg="white", xalign=0)

football_section = Image.from_column([sectiontext("From the word football"), football_boxes], bg="white", xalign=0, padding=(0,5))

other_boxes = Image.from_array([
[box(PALETTE[4]), boxtext("From soccer (short for association)")],
[box(PALETTE[5]), boxtext("From a word or phrase meaning 'kick'")]
], bg="white", xalign=0)

other_section = Image.from_column([sectiontext("From another source"), other_boxes], bg="white", xalign=0, padding=(0,5))

legend = Image.from_column([football_section, other_section], bg="white", xalign=0, padding=5).pad(1, "black")
chart = map.place(legend, align=(1,0), padding=10)

title = Image.from_column([
Image.from_text("EUROPEAN NAMES FOR THE BEAUTIFUL GAME", arial(48, bold=True)),
Image.from_text("etymologies of association football in different European languages", arial(36))],
bg="white")

img = Image.from_column([title, chart], bg="white", padding=2)
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/etymfootball.png")
