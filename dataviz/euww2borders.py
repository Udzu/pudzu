from pudzu.charts import *
from pudzu.pillar import sans

GREENS = ["#c7e9c0ff", "#a1d99bff", "#74c476"]
REDS = ["#fcbba1", "#fc9272", "#fb6a4a", "#ef3b2c", "#cb181d", "#a50f15"]

boxes = []
for g,r in zip_longest(GREENS, REDS):
    box = Image.from_row([Rectangle(36, r), Rectangle(36, g)])
    boxes.append(box)

map = Image.open("output/euww2borders.png").remove_transparency("white").trim((0,0,15,0))

legend = generate_legend(
    boxes,
    ["under 1%", "1% to 5%", "5% to 10%", "10% to 15%", "15% to 20%", "20% to 25%"],
    font_family = partial(sans, 16),
    header="% area lost (red) or gained (green)")

df = pd.read_csv("datasets/euww2area.csv")
df["change"] = 100 * (df["area_1948"] / df["area_1936"] - 1)
df = df.sort_values("change")
df = df.set_index("country")
fdf = df
df = df[df["change"] ** 2 > 0.1]

flags = pd.read_csv("../dataviz/datasets/countries.csv").split_columns(('country'), "|").explode('country').set_index('country').flag
flags["USSR"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a9/Flag_of_the_Soviet_Union.svg/1024px-Flag_of_the_Soviet_Union.svg.png"
flags["Czechoslovakia"] = flags["Czech Republic"]
flags["Yugoslavia"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/6/61/Flag_of_Yugoslavia_%281946-1992%29.svg/1024px-Flag_of_Yugoslavia_%281946-1992%29.svg.png"

def color(c, r, v):
    cols = REDS[::-1] + GREENS
    vals = (-20, -15, -10, -5, -1, 0, 1, 5, 10, 15)
    i = next(i for i,lim in enumerate(vals) if v <= lim)
    return cols[i]

def rlabel(r):
    return Image.from_url_with_cache(flags[df.index[r]]).convert("RGBA").resize((40,28)).trim(1).pad(1, "grey")
    # return Image.from_column([
    #     Image.from_url_with_cache(flags[df.index[r]]).convert("RGBA").resize((50,30)).trim(1).pad(1, "grey"),
    #     Image.from_text(df.index[r], sans(12, bold=False), "black", max_width=55)
    # ], bg="white", padding=(0,2))

bar = bar_chart(df[["change"]], 30, 750, horizontal=True, ymin=-25.01, ymax=10, grid_interval=5, label_font=sans(16), clabels=None,
        ylabels="{:+.0f}%", #rlabels=rlabel,
          colors=color).pad((0,10), bg="white")


img = Image.from_column([map.place(legend, 0), bar], bg="white")

title = Image.from_text_bounded("European country size changes\nbetween 1936 and 1949".upper(), img.size, 60, partial(sans, bold=True), align="center")
subtitle = Image.from_text_bounded("(labelled with the biggest contributing border changes)", [round(img.width*0.8), img.height], 60, partial(sans, italics=True))
img = Image.from_column([title, subtitle, img], bg="white", padding=10)

img.place(Image.from_text("/u/Udzu", sans(16), padding=5).pad((1,1,0,0), "black"), align=1, padding=5, copy=False)

img.save("output/euww2borders2.png")