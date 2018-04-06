import sys
sys.path.append('..')
from charts import *

FONT = calibri
df = pd.read_csv("datasets/euenlargement.csv").set_index("year")
for i in range(1950, 2020):
    if i not in df.index:
        df.loc[i] = df.area[i-1], ""
df = df.sort_index()
# df = df.update_columns(area = lambda x: x / 9525067)

# def rlabel(r):
    # return Image.from_column([
        # Image.from_url_with_cache(atlas.flag[df.index[r]]).convert("RGBA").resize((50,30)).trim(1).pad(1, "grey"),
        # Image.from_text(df.index[r], arial(12, bold=False), "black", max_width=55)
    # ], bg="white", padding=(0,2))

def label(x): return Image.from_text(str(x), FONT(12)).transpose(Image.ROTATE_90)
    
chart = bar_chart(df[['area']], 20, 600, spacing=0, label_font=FONT(14),
    colors=lambda c,r,v: "#e41a1c" if df.label[df.index[r]].startswith("−") else "#4daf4a" if df.label[df.index[r]] else "#003399",
    clabels={ BarChartLabelPosition.INSIDE: lambda c,r,v,w,h: "" if df.label[df.index[r]].startswith("−") or "ux" in df.label[df.index[r]] else Rectangle((w,h),0).place(label(" " + get_non(df.label, df.index[r], "")), align=(0.5,1)),
              BarChartLabelPosition.OUTSIDE: lambda c,r,v: "" if not (df.label[df.index[r]].startswith("−") or "ux" in df.label[df.index[r]]) else label(" " + get_non(df.label, df.index[r], "")) },
    rlabels=lambda r: label(df.index[r]),
    # grid_interval=0.05, label_interval=0.1, ylabels=lambda v: "{:.0f}%".format(v*100),
    grid_interval=500000, label_interval=1000000, ylabels=lambda v: "{}m".format(v//1000000),
    ylabel=Image.from_text("area in km² (for comparison, the USA is 9.8m km²)", FONT(18), padding=(5,2,5,10), bg="white").transpose(Image.ROTATE_90),
    xlabel=Image.from_text("year", FONT(18), padding=5)
    )
    
title = Image.from_column([
    Image.from_text("the changing area of the European Union".upper(), arial(40, bold=True)),
    Image.from_text("enlargements and reductions of the ECSC/EEC/EU", arial(32, italics=True))
    ], bg="white", padding=2)

img = Image.from_column([title, chart], bg="white", padding=8)
img.place(Image.from_text("/u/Udzu", font("arial", 12), fg="grey", bg="white", padding=5).pad((1,1,0,0), "grey"), align=1, padding=5, copy=False)
img.save("output/euenlargement.png")