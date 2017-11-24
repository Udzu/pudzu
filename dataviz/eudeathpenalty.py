import sys
sys.path.append('..')
from charts import *
from bamboo import *
import seaborn as sns

# generate map
df = pd.read_csv("datasets/eudeathpenalty.csv").set_index("country")
palette = ImageColor.from_floats(sns.color_palette())
methods = sorted(set(x for x in df.method if not non(x)))

def colorfn(c):
    if c not in df.index or non(df.method[c]): return "white" if c in ['Sea', 'Borders'] else "grey"
    return palette[methods.index(df.method[c])]
    
def labelfn(c, w, h):
    if c not in df.index or non(df.year[c]): return None
    return Image.from_text_bounded(df.year[c], (w, h), 24, arial)
    
map = map_chart("maps/Europe.png", colorfn, labelfn)

# legend
legendboxes = Image.from_array([
[Image.new("RGBA", (40,40), palette[i]), Image.from_text(methods[i].title(), arial(16))] for i in range(len(methods))] + [
[Image.new("RGBA", (40,40), "grey"), Image.from_text("No data", arial(16))]
], xalign=(0.5, 0), padding=(3,0), bg="white")

legend = Image.from_column([
Image.from_text("Methods", arial(16, bold=True), padding=5),
legendboxes,
Image.from_text("* Sweden used a guillotine for its last execution, but beheading before.\n\n* Spain used a firing squad for its last execution, but garrotte before.", arial(16, italics=True), align="left", max_width=150, padding=(0,0,0,2))
], bg="white", xalign=0, padding=(0,2)).pad(5, "white").pad(1, "black")
chart = map.place(legend, align=(1,0), padding=10)

# title
title = Image.from_column([
Image.from_text("DEATH PENALTY IN EUROPE", arial(48, bold=True)),
Image.from_text("method and year of last peacetime execution", arial(36))],
bg="white")

# title = Image.from_text("Europe by number of, and longest borders", arial(48, bold=True), bg="white")
img = Image.from_column([title, chart], bg="white", padding=2)
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/eudeathpenalty.png")
