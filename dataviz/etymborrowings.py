import sys
sys.path.append('..')
from charts import *
from bamboo import *
import seaborn as sns

# generate map
df = pd.read_csv("datasets/etymborrowings.csv").set_index("language").assign_rows(word_lc=lambda d: d.word.lower()).sort_values("word_lc")

PALETTE = ImageColor.from_floats(sns.color_palette())

def colorfn(c):
    if c in ['Sea', 'Language Borders']: return "white"
    elif c in ['English']: return PALETTE[2]
    elif not get_non(df.word, c): return "grey"
    else: return PALETTE[0]
    
def labelfn(c, w, h):
    if not get_non(df.word, c): return None
    label = df.word[c]
    return Image.from_text_bounded(label, (w, h), 24, papply(arial, bold=True), align="center", padding=(0,0,0,2))
    
map = map_chart("maps/Eurolang.png", colorfn, labelfn)

legendfont=24
legendtext = Image.from_array([
[Image.from_text("{}:".format(d.word), arial(legendfont, bold=True), padding=(0,0,0,4)),
 Image.from_text(get_non(d, 'origin', "?"), arial(legendfont), padding=(0,0,0,4), max_width=500)] for _,d in df.iterrows()],
bg="white", padding=(4,2), xalign=(1,0))

legend = Image.from_column([
Image.from_text("Word etymologies".upper(), arial(legendfont, bold=True), padding=(0,0,0,4)),
legendtext], bg="white", xalign=0).pad(5,"white").pad(1,"black")

chart = Image.from_row([map, legend], bg="white", padding=10, yalign=0)

title = Image.from_column([
Image.from_text("English words from various European languages".upper(), arial(48, bold=True)),
Image.from_text("with an emphasis on widely-used words over localised currencies, food, music, etc", arial(36, italics=True))], # currencies, food and dances
bg="white")

img = Image.from_column([title, chart], bg="white", padding=2)
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/etymborrowings.png")
