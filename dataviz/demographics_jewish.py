from pudzu.charts import *
from pudzu.experimental.bamboo import *

atlas = pd.read_csv("datasets/countries.csv").split_columns('country', "|").explode('country').set_index("country")
df = pd.read_csv("datasets/demographics_jewish.csv").set_index("country").sort_values("historical", ascending=False).fillna(0)

def rlabel(r):
    return Image.from_column([
        Image.from_url_with_cache(atlas.flag[df.index[r]]).convert("RGBA").resize((50,30)).trim(1).pad(1, "grey"),
        Image.from_markup(df.city[r].replace("\\n","\n"), partial(arial, 12), "black", max_width=55, align="center", hyphenator=language_hyphenator())
    ], bg="white", padding=(0,2))

def clabel_inside(c,r,v,w,h):
    if c == 0 and v > 3.5:
        return Rectangle((w,h),0).place(Image.from_text("({})".format(int(df.year[r])), arial(10), padding=(0,2)), (0.5,0))
    if c == 1 and v >= 1.5:
        return "{:.2g}%".format(v)
    return None
    
def clabel_outside(c,r,v):
    if c == 0 or (v < 1.5 and df.historical[r] >= 3.5): 
        return "{:.2g}%".format(v)
    return None
    
chart = bar_chart(df[["historical", "current"]], 50, 500, type=BarChartType.OVERLAYED, spacing=2, label_font=arial(12),
    clabels={ BarChartLabelPosition.OUTSIDE: clabel_outside, BarChartLabelPosition.INSIDE: clabel_inside },
    rlabels=rlabel, grid_interval=10, ylabels="{}%",
    legend_position=(1,0), legend_fonts=papply(arial, 14), legend_box_sizes=30, legend_args={"header": "Jewish populations", "labels": ["Historical estimate (year in brackets)", "Current estimate"]},
    ylabel=Image.from_text("Jewish % of city population", arial(14), padding=(5,2,5,10), bg="white").transpose(Image.ROTATE_90))
    
title = Image.from_column([
    Image.from_text("The disappearance of Europe's urban Jewish population ".upper(), arial(36, bold=True)),
    Image.from_text("major national cities with historical Jewish populations of over 2%, compared to now", arial(28, italics=True)),
    Image.from_text("causes include the Holocaust (which killed ~60% of Europe's Jews) as well as political and economic migration, assimilation and urbanisation", arial(16))
    ], bg="white", padding=2)
footer = Image.from_markup("data is from a variety of sources and should be viewed as approximate; cities marked with * are second-largest cities that had a significantly larger Jewish population than the largest one", partial(arial, 14))

img = Image.from_column([title, chart, footer], bg="white", padding=5)
img.place(Image.from_text("/u/Udzu", font("arial", 12), fg="grey", bg="white", padding=5).pad((1,1,0,0), "grey"), align=1, padding=5, copy=False)
img.save("output/demographics_jewish.png")