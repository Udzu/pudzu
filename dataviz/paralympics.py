from pudzu.charts import *
from pudzu.sandbox.bamboo import *

atlas = pd.read_csv("datasets/countries.csv").split_columns('country', "|").explode('country').set_index("country")


resp = requests.get("https://en.m.wikipedia.org/wiki/All-time_Paralympic_Games_medal_table")
dfs = pd.read_html(resp.content.replace(b'"5;"',b'"5"'))
df = dfs[0]
df = df.drop(df.columns[6:], axis=1)
df.columns = ["name", "number", "gold", "silver", "bronze", "total"]

df["country"] = df[df.columns[0]].apply(lambda x: re.sub("\s\(.*\)","",x)).apply(lambda x: re.sub("\[\d+\]","",x))
df["continent"] = df.country.apply(lambda x: atlas.continent.get(x, "Unknown"))
df["population"] = df.country.apply(lambda x: atlas.population.get(x, 0))

df = df[((df.continent == "Europe") | (df.country.isin(["Azerbaijan", "Turkey", "Armenia", "Georgia", "Kazakhstan"]))) & (df.total > 0)].set_index("country").drop(["name", "continent"], 1)
df["total_pc"] = df.total / df.population * 1000000 / df.number
df["minus_total_pc"] = -df.total_pc

df = df.sort_values(["total_pc", "total"], ascending=False) 

df["label"] = 80

W, H = 60, 40
PALETTE = ["#fcc900", "#d3d3d3", "#d26c00", "#00000000"]

def rlabel(r):
    flag = Image.from_url_with_cache(atlas.flag[df.index[r]]).convert("RGBA")
    flag = flag.resize_fixed_aspect(height=H) if flag.width / flag.height < 1.1 else flag.resize((W,H))
    return Image.from_column([
    flag.trim(1).pad(1, "grey"),
    Image.from_text(f"({df.number[r]})", sans(16), VegaPalette10.RED),
    ])

chart1 = bar_chart(df[["gold", "silver", "bronze", "label"]], W, 600, BarChartType.STACKED, colors=PALETTE, grid_interval=100, label_font=sans(14), label_interval=200, 
    rlabels=rlabel, spacing=1,
    ylabel=Image.from_text("# medals won", sans(16), padding=10).transpose(Image.ROTATE_90),
    clabels = lambda c,r,v: str(v) if c < 3 else str(df.total[df.index[r]]),
#    clabels=lambda c,r,v: f(v),
#    ylabel=Image.from_text("weighted number of medals won", sans(16), padding=5).transpose(Image.ROTATE_90)
)


chart2 = bar_chart(df[["minus_total_pc"]], W, 300, ymin=-10, grid_interval=1, label_font=sans(14), label_interval=2, 
    rlabels=None, clabels={BarChartLabelPosition.INSIDE: lambda c,r,v: f"{abs(v):.1f}"},
    ylabels=lambda v: str(abs(v)), spacing=1,
    ylabel=Image.from_text("# medals per million per Games", sans(16), padding=10).transpose(Image.ROTATE_90),
#    clabels=lambda c,r,v: f(v),
#    ylabel=Image.from_text("weighted number of medals won", sans(16), padding=5).transpose(Image.ROTATE_90)
)

chart = Image.from_column([chart1, chart2.pad((12,0,0,0), "white")], bg="white")

title = Image.from_text("European countries at the Summer Paralympics".upper(), sans(64, bold=True), padding=20)
subtitle = Image.from_text("all-time medals won per country (and number of Games competed in in parentheses)", sans(32, italics=True), VegaPalette10.RED, padding=0)
titles = Image.from_column([title, subtitle], bg="#FFFFFFAA")
img = chart.place(titles, align=(0.5,0))
img = img.pad((0,20,20,20), "white")
img.place(Image.from_text("/u/Udzu", font("arial", 12), fg="grey", bg="white", padding=5).pad((1,1,0,0), "grey"), align=1, padding=5, copy=False)

img.save("output/paralympics.png")

