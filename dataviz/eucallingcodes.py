from pudzu.charts import *
from pudzu.bamboo import *
import seaborn as sns

# generate map
atlas = pd.read_csv("datasets/countries.csv").split_columns('country', "|").explode('country').set_index('country')


CATEGORIES = { 2: "Africa", 3: "Europe", 4: "Europe", 7: "Soviet Union", 9: "Asia"}
PALETTE = tmap(RGBA, sns.color_palette())

def colorfn(c):
    if c in ['Sea', 'Borders']: return "white"
    else: return PALETTE[sorted(CATEGORIES.keys()).index(int(atlas.callingcode[c][1]))]
    
def labelfn(c, w, h):
    if c not in atlas.index: return None
    label = atlas.callingcode[c]
    maxsize = 48 if len(label) == 2 else 28 if len(label) == 3 else 20
    return Image.from_text_bounded(atlas.callingcode[c], (w, h), maxsize, papply(arial, bold=True), align="center", padding=(0,0,0,2))
    
map = map_chart("maps/Europe.png", colorfn, labelfn)

# # legend

def box(c, s, box_size=40): return Image.new("RGBA", (box_size, box_size), c).place(Image.from_text(s, arial(16, bold=True), fg="white"))
def boxtext(s, fg="black"): return Image.from_text(s, arial(16), padding=(10,0,0,3), max_width=150, align="left", fg=fg)
def sectiontext(s): return Image.from_text(s.upper(), arial(16, bold=True))

boxes = Image.from_array([
[box(PALETTE[0], "+2"), boxtext("Africa")],
[box(PALETTE[1], "+3"), boxtext("Europe #1")],
[box(PALETTE[2], "+4"), boxtext("Europe #2")],
[box(PALETTE[3], "+7"), boxtext("USSR")],
[box(PALETTE[4], "+9"), boxtext("Asia")]
], bg="white", xalign=0)

section = Image.from_column([sectiontext("Zones"), boxes], bg="white", xalign=0, padding=(0,5))

legend = Image.from_column([section], bg="white", xalign=0, padding=5).pad(1, "black")
chart = map.place(legend, align=(1,0), padding=10)

title = Image.from_column([
Image.from_text("country calling codes in Europe".upper(), arial(48, bold=True)),
Image.from_text("(aka Turkey in Asia, Russia in USSR and Faroe Islands in Africa?!)", arial(36))],
bg="white")

img = Image.from_column([title, chart], bg="white", padding=2)
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/eucallingcodes.png")
