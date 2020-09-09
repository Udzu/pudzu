from pudzu.charts import *
from pudzu.sandbox.bamboo import *

FONT = sans

flags = pd.read_csv("datasets/countries.csv").split_columns('country', "|").explode('country').set_index('country').flag
df = pd.read_csv("datasets/continents.csv").set_index("continent")

df["pop_pc"] = df.pop_m / df.pop_total
df["area_pc"] = df.area_k / df.area_total

def flag(f, right):
    fl = Image.from_url_with_cache(flags[f]).to_rgba().resize((90,60)).trim(1).pad(1, "grey")
    l = Image.from_text(f, FONT(16, bold=False))
    return Image.from_row([fl, l] if not right else [l, fl], padding=(5,0))
def clabel(v): return Image.from_text(str(v), FONT(16), "white")
def roundish(v): return int(v) if v > 100 else v

area_chart = bar_chart(df[['area_pc']], 60, 600, ymax=1, grid_interval=0.1, label_interval=0.1, clabels={BarChartLabelPosition.INSIDE: lambda c,r,v: clabel('{:.3}m{}'.format(df.area_k[r]/1000, " km²"*(df.area_k[r]>3000)))}, label_font=FONT(16), horizontal=True, spacing=1, rlabels={BarChartLabelPosition.ABOVE: lambda r: flag(df.area[r], False)}, ylabel=Image.from_text("proportion of continent’s area", FONT(24), padding=2), colors=[VegaPalette10.ORANGE], ylabels=lambda v: "{0:.0%}".format(abs(v)))
pop_chart = bar_chart(-df[['pop_pc']], 60, 600, ymin=-1, grid_interval=0.1, label_interval=0.1, clabels={BarChartLabelPosition.INSIDE: lambda c,r,v: clabel('{}m'.format(roundish(df.pop_m[r])))}, label_font=FONT(16), horizontal=True, spacing=1, rlabels={BarChartLabelPosition.BELOW: lambda r: flag(df.population[r], True), BarChartLabelPosition.ABOVE: lambda r: Image.from_text(str(df.index[r].upper()), FONT(16, bold=True))}, ylabel=Image.from_text("proportion of continent’s population", FONT(24), padding=2), colors=[VegaPalette10.BLUE], ylabels=lambda v: "{0:.0%}".format(abs(v)))
chart = Image.from_row([pop_chart, area_chart], yalign=1, bg="white")


TITLE = "Largest countries per continent"

title = Image.from_text_bounded(TITLE.upper(), chart.size, 80, partial(FONT, bold=True))

FOOTER = "*includes only the landmasses on the Australian plate, though adding the rest of the Oceania region doesn't make much difference."
footer = Image.from_text_bounded(FOOTER, chart.size, 16, partial(FONT, italics=True))

img = Image.from_column([title, chart, footer], bg="white", padding=20)
img.place(Image.from_text("/u/Udzu", font("arial", 14), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/continents.png")

