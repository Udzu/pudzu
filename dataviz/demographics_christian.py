import sys

sys.path.append('..')
from charts import *
from bamboo import *

atlas = pd.read_csv("datasets/countries.csv").split_columns('country', "|").split_rows('country').set_index('country')
df = pd.read_csv("datasets/demographics_christian.csv").set_index("country").sort_values("in 1910", ascending=False)

def rlabel(r):
    return Image.from_column([
        Image.from_url_with_cache(atlas.flag[df.index[r]]).convert("RGBA").resize((50,30)).trim(1).pad(1, "grey"),
        Image.from_text(df.index[r], arial(12, bold=False), "black", max_width=55)
    ], bg="white", padding=(0,2))

chart = bar_chart(df, 50, 500, type=BarChartType.OVERLAYED, spacing=2, label_font=arial(12),
    clabels=lambda c,r,v: None if df.index[r] == "Iran" and v == 0.4 else "{}%".format(v),
    rlabels=rlabel, grid_interval=10, ylabels="{}%",
    legend_position=(1,0), legend_fonts=papply(arial, 14), legend_box_sizes=30, legend_args={"header": "Percentages"},
    ylabel=Image.from_text("% of population that is Christian", arial(14), padding=(5,2,5,10), bg="white").transpose(Image.ROTATE_90))
    
title = Image.from_column([
    Image.from_text("The falls and rises of Christianity in the Middle East".upper(), arial(28, bold=True)),
    Image.from_text("Christian population percentages by country: 1910 versus 2010*", arial(24, italics=True))
    ], bg="white", padding=2)
footer = Image.from_markup("* Data from [[http:\\//www.gordonconwell.edu/ockenga/research/documents/JMEPP-JohnsonaandZurlo.pdf]].", partial(arial, 14))

img = Image.from_column([title, chart, footer], bg="white", padding=8)
img.place(Image.from_text("/u/Udzu", font("arial", 12), fg="grey", bg="white", padding=5).pad((1,1,0,0), "grey"), align=1, padding=5, copy=False)
img.save("output/demographics_christian.png")