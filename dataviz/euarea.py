import sys

sys.path.append('..')
from charts import *
from bamboo import *

atlas = pd.read_csv("datasets/countries.csv").split_columns('country', "|").split_rows('country').set_index('country')
df = pd.read_csv("datasets/euarea.csv").set_index("country").assign_rows(ratio=lambda d: d.european / d.overall).sort_values("ratio", ascending=True).fillna(" ")
ylabel = Image.from_text("% of area in Europe", arial(14), padding=(5,2,5,10), bg="white").transpose(Image.ROTATE_90)

def rlabel(r):
    if "Union" in df.index[r]: name = "rest of Europe**"
    else: name = df.index[r] + "*" * int(df.index[r] in ["Denmark", "Russia"])
    return Image.from_column([
Image.from_url_with_cache(atlas.flag[df.index[r]]).resize((80,60)).pad(1, "grey").pad((0,5), "white"),
Image.from_text(name, arial(14, bold=False), "black", align="center", padding=1),
Image.from_text(df.description[r] if df.description[r] == " " else "({})".format(df.description[r].replace("\\n","\n")), arial(10, bold=False), "black", align="center", padding=1)
], bg="white")
def clabel(c,r,v): return Image.from_text("{:.1%}".format(v), arial(14, bold=False), "white")
def clabel_overflow(c,r,v): return None if v > 0 else "0%"
    
chart = bar_chart(df[['ratio']], 90, 600, 
    spacing=5, ymax=1, colors=["#003399"], rlabels=rlabel, clabels={ BarChartLabelPosition.INSIDE : clabel, BarChartLabelPosition.OUTSIDE : clabel_overflow},
    grid_interval=0.1, label_interval=0.1, label_font=arial(14, bold=False), ylabels="{:.0%}", ylabel=ylabel)

title = Image.from_column([
Image.from_text("% of European countries’ area which is in Europe".upper(), arial(40, bold=True), padding=(5,10,5,2)),
Image.from_text("using the Bosporus/Caucasus/Ural definition of Europe, and grouping islands with nearby continents", arial(24, bold=False), padding=(5,2,5,10))], bg="white")

footer = Image.from_text("* most of the populations of Russia and Denmark live in Europe. ** <0.1% of the area of Italy is off Africa; countries’ Antarctic claims are excluded.", arial(14), "black", padding=10)

img = Image.from_column([title, chart, footer], bg="white")
img.place(Image.from_text("/u/Udzu", font("arial", 14), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/eueara.png")