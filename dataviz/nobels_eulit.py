from pudzu.charts import *
from pudzu.sandbox.bamboo import *

atlas = pd.read_csv("datasets/countries.csv").split_columns('country', "|").explode('country').set_index('country')
atlas.flag["Yugoslavia"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e5/Flag_of_Yugoslavia_%281918%E2%80%931941%29.svg/1024px-Flag_of_Yugoslavia_%281918%E2%80%931941%29.svg.png"
df = pd.read_csv("datasets/nobels_eulit.csv").split_columns(('winners', 'countries'), "|")
df["count"] = df.winners.apply(len)
df = df.sort_values(["count", "language"], ascending=[False,True]).set_index("language")
counts = df[["count"]]

# TODO: count by type, add two types and sort
# counts = df.groupby("country").count()
# counts["sort"] = counts.description - 10 * counts.index.isin(["latin", "greek"])
# counts = counts.sort_values("sort", ascending=False)[['symbol']]
#
# gb = df.groupby(["country", "type"]).count()[["symbol"]]
# counts = gb.symbol.unstack(level=1).fillna(0)
# counts["sort"] = counts.b + counts.d + counts.n - 10 * counts.index.isin(["latin", "greek"])
# counts = counts.sort_values(["sort", "b"], ascending=False).drop("sort", axis=1)
#
# # ylabel = Image.from_text("% of area in Europe", arial(14), padding=(5,2,5,10), bg="white").transpose(Image.ROTATE_90)
#
def resize_flag(img):
    if img.width / img.height < 1.3: return img.resize_fixed_aspect(height=60)
    else: return img.resize((90,60))

def rlabel(r):
    countries = df.countries[counts.index[r]]
    print(countries)
    flag_urls = [atlas.flag[c] for c in countries]
    label = Image.from_text_bounded(counts.index[r].upper(), (100,100), 16, partial(sans, bold=True), padding=(0,5))
    flags = [resize_flag(Image.from_url_with_cache(flag).to_rgba()).pad(1,"grey") for flag in flag_urls]
    return Image.from_column([label]+flags, padding=(0,2), bg="white")

def clabel(c,r,v,w,h):
    names = df.winners[counts.index[r]]
    def box(w,h,name):
        return Rectangle((w,h), 0).place(Image.from_text(name, sans(14, italics=True), beard_line=True))
    return Image.from_column([box(w,h//len(names),name) for name in reversed(names)])

chart = bar_chart(counts, 100, 800,
    spacing=5, ymax=15, rlabels=rlabel, clabels={ BarChartLabelPosition.INSIDE : clabel },
    grid_interval=1, label_interval=1, label_font=sans(14, bold=False),
)

title = Image.from_text("European Nobel laureates in Literature by language".upper(), sans(60, bold=True), padding=20)

footer = Image.from_text("""*Andrić was born in Bosnia to Croatian parents and wrote mainly in Serbian; Bunin, Sachs, Canetti and Singer emigrated to France, Sweden, UK and US but continued to write in their native languages.
Xingjian, Naipaul and Vargas Llosa also had French, British and Spanish citizenship, but are not usually viewed as European writers; neither are the European-born White and Agnon.""", sans(18), "black", padding=10)

img = Image.from_column([title, chart.pad(20, "white")], bg="white")
img.place(footer, align=(0.5,1), padding=10, copy=False)
img.place(Image.from_text("/u/Udzu", sans(14), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)

img.save("output/nobels_eulit.png")
