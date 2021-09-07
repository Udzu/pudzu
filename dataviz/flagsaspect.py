from pudzu.charts import *
from statistics import mean
from colorsys import rgb_to_hls, hls_to_rgb

flags = pd.read_csv("datasets/countries.csv").filter_rows("organisations >> un").update_columns(country=lambda s: s.split("|")[0]).set_index("country").flag

W,H = 80, 40

bg = "#BBBBBBFF"

ratios = {}
actual_ratios = {}
for c,f in flags.items():
    flag = Image.from_url_with_cache(f)
    ar = flag.width / flag.height + 0.000001
    ratios.setdefault(round(ar, 1), set()).add(c)
    actual_ratios.setdefault(ar, set()).add(c)

df = pd.DataFrame([len(ratios.get(ar/10, [])) for ar in range(1, 26)], index=range(1, 26))

def clabel(c,r,v, x, y):
    countries = sorted(ratios.get(df.index[r]/10, []), reverse=True)
    flagimgs = [Rectangle((W,H),None).place(Image.from_url_with_cache(flags[c]).to_rgba().resize_fixed_aspect(width=W-2, height=H-2).pad(1, bg)) for c in countries]
    bar = Image.from_column(flagimgs) if flagimgs else None
    return bar

chart = bar_chart(df, W, H*87, spacing=5,
                  ymax=87, grid_interval=5, colors=[bg],
                  clabels={ BarChartLabelPosition.INSIDE : clabel },
                  rlabels = lambda v: str(df.index[v]/10),
                  xlabel=Image.from_text("flag aspect ratio (rounded to nearest 0.1)", sans(36, bold=False), padding=20),
                  label_font=sans(24),
)

title = Image.from_text("Flags of the world by aspect ratio".upper(), verdana(92, bold=True), padding=(0,0,0,2))
subtitle = Image.from_text("195 UN member and observer states, based on flag images on Wikipedia", verdana(60, italics=True), padding=(0,0,0,20))
img = Image.from_column([title, subtitle, chart], bg="white", padding=5).pad(10, "white")
img.place(Image.from_text("/u/Udzu", sans(24), fg="grey", bg="white", padding=5).pad((1,1,0,0), "grey"), align=1, padding=5, copy=False)
img.save("output/flagsaspect.png")


