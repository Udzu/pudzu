from pudzu.charts import *
from pudzu.bamboo import *
import seaborn as sns

# generate map
df = pd.read_csv("datasets/euborders.csv")
counts = df.groupby_rows(lambda d: min(10, d["borders"])).count()['country']
df = df.set_index('country')

palette = tmap(RGBA, sns.cubehelix_palette(11, start=0.2, rot=-0.75))

def colorfn(c):
    if c not in df.index:
        return "white" if c in ['Sea', 'Borders'] else "grey"
    return palette[min(10, df['borders'][c])]
    
map = map_chart("maps/Europe.png", colorfn, ignoring_exceptions(lambda c: str(get_non(df.loc[c], "longest", ""))), label_font=arial(12, bold=True))

# generate legend
font_size = 16
def box(c, label, box_size=30): return Image.new("RGBA", (box_size, box_size), c).place(Image.from_text(label, arial(font_size, bold=True), "white", bg=c))
def stripebox(c1, c2, box_size=30): return Image.from_pattern(stripe(c1, c2), (box_size,box_size))

year_arr = Image.from_array([
[box(palette[i], str(counts[i])), Image.from_text("10+" if i == 10 else "none" if i == 0 else str(i), arial(font_size), padding=(10,0))] for i in range(11)
], bg="white", xalign=0)
year_leg = Image.from_column([Image.from_text("# neighbours", arial(font_size, bold=True)), year_arr], bg="white", xalign=0, padding=(0,5))

note_leg = Image.from_text("Russia (14) and France (11) are top. Labels show longest border. France is France entière.", arial(font_size), max_width=120, bg="white", padding=(0,2))
legend = Image.from_column([year_leg, note_leg], bg="white", xalign=0, padding=5).pad(1, "black")
chart = map.place(legend, align=(1,0), padding=10)

# title
title = Image.from_column([
Image.from_text("BORDERS IN EUROPE", arial(48, bold=True)),
Image.from_text("number of and longest land borders", arial(36))],
bg="white")

# title = Image.from_text("Europe by number of, and longest borders", arial(48, bold=True), bg="white")
img = Image.from_column([title, chart], bg="white", padding=2)
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/euborders.png")
