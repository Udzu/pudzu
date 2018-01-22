import sys
sys.path.append('..')
from charts import *

atlas = pd.read_csv("datasets/countries.csv").split_columns('country', "|").split_rows('country').set_index("country")
df = pd.read_csv("datasets/g7_policedeaths.csv").set_index("country")
df["policedeaths_pm"] = df["policedeaths_total"] * 1000000 / atlas.loc[df.index].population

def label_if(pred, labeler=lambda c,r,v: format_float(v, 3)):
    return lambda c,r,v: None if not pred(v) else labeler(c,r,v)

def rlabel(r):
    return Image.from_row([
        Image.from_text(df.index[r].replace("\\n","\n"), arial(16), "black", align="center"),
        Image.from_url_with_cache(atlas.flag[df.index[r]]).convert("RGBA").resize((60,40)).trim(1).pad(1, "grey")
    ], bg="white", padding=(2,0))

df = df.sort_values("guns_ph", ascending=False)
guns = bar_chart(df[["guns_ph"]], 40, 350, horizontal=True, spacing=2, label_font=arial(16), rlabels=rlabel,
                  clabels= { BarChartLabelPosition.INSIDE : label_if(artial(op.ge,15)), BarChartLabelPosition.OUTSIDE: label_if(artial(op.lt,15)) },
                  grid_interval=10, ymax=101, ylabel=Image.from_text("privately owned guns per 100 population (2007)", arial(18), padding=5))

df = df.sort_values("homicide_pm", ascending=False)
homicides = bar_chart(df[["homicide_pm"]], 40, 350, horizontal=True, spacing=2, label_font=arial(16), rlabels=rlabel,
                  clabels= { BarChartLabelPosition.INSIDE : label_if(artial(op.ge,2)), BarChartLabelPosition.OUTSIDE: lambda c,r,v: "(lower than the US police's killing rate)" if df.index[r] == "Japan" else None },
                  grid_interval=5, ymax=40, ylabel=Image.from_text("intentional homicides per million population (2015)", arial(18), padding=5))

df = df.sort_values("policedeaths_pm", ascending=False)
policedeaths = bar_chart(df[["policedeaths_pm"]], 40, 850, horizontal=True, spacing=2, label_font=arial(16), rlabels=rlabel,
                  clabels= { BarChartLabelPosition.INSIDE : label_if(artial(op.ge,0.5), lambda c,r,v: "{:.2g} ({} total)".format(v, df.policedeaths_total[df.index[r]])),
                             BarChartLabelPosition.OUTSIDE: label_if(artial(op.lt,0.5), lambda c,r,v: "{:.1g} ({} total)".format(v, df.policedeaths_total[df.index[r]])) },
                  grid_interval=0.5, ymax=3.5, ylabel=Image.from_multitext(["killings by law enforcement officers per million population (2015) ", "(estimates apart from UK and Germany)"], [arial(18), arial(14)]).pad(5,0))
                  
chart = Image.from_column([policedeaths, Image.from_row([guns, homicides])], bg="white", padding=10)
title = Image.from_column([Image.from_text("Police killing rates in G7 countries".upper(), arial(36, bold=True)), Image.from_text("compared to gun ownership and homicide rates", arial(32))])
footer = Image.from_text("Police killing data from a variety of sources. All other data from Wikipedia.", arial(16), padding=5)

img = Image.from_column([title, chart, footer], padding=5, bg="white")
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/g7_police.png")
