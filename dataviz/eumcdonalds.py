import sys
sys.path.append('..')
from charts import *
from bamboo import *
import seaborn as sns

# data
df = pd.read_html("https://en.wikipedia.org/wiki/List_of_countries_with_McDonald%27s_restaurants")[1]
df = df.rename(columns=df.iloc[0])[1:].fillna("0")
df = df.assign_rows(year=lambda d: re.search("((?:19|20)\d\d)", d["Date of first store"] + " 2019").group(0),
                    country=lambda d: d["Name of country"].split(" (")[0],
                    number=lambda d: int(d["Number of currently operating outlets"].split("[")[0].split("+")[0]),
                    percapita=lambda d: int(d["People per outlet"].translate({ord(c): None for c in ">,"})))
df["permillion"] = 1000000 / df["percapita"]
df = df[["country", "year", "number", "permillion"]].set_index("country")

# map
LIMITS = [20, 10, 5, 2, 0]
REDS = treversed(tmap(RGBA, sns.color_palette("Reds", len(LIMITS))))

def colorfn(c):
    c = {"UK": "United Kingdom", "Bosnia": "Bosnia and Herzegovina"}.get(c, c)
    if c in ['Sea', 'Borders']: return "white"
    elif c in ['Macedonia', 'Montenegro', 'Iceland']: return VegaPalette10.BLUE
    elif c not in df.index: return "#AAAAAA"
    else: return REDS[next(i for i,lim in enumerate(LIMITS) if df.permillion[c] > lim)]
    
def labelfn(c, w, h):
    c = {"UK": "United Kingdom", "Bosnia": "Bosnia and Herzegovina"}.get(c, c)
    if c in df.index: label = "**{} McD's**\n(//{}{}–//)".format(df.number[c], df.year[c], "*"*int(c=="Portugal"))
    else: label = {"Macedonia": "(//1997–\n2013//)", "Iceland": "(//1993–\n2009//)", "Montenegro": "(//2004–\n2007//)"}.get(c, " ")
    return Image.from_text_bounded(label, (w,h), 24, partial(partial, arial), align="center", generator=Image.from_markup)
    
map = map_chart("maps/Europe.png", colorfn, labelfn)
legend = generate_legend(REDS + (VegaPalette10.BLUE,"#AAAAAA"), ["{}+ per million".format(i) for i in LIMITS[:-1]] + ["<{} per million".format(LIMITS[-2]), "former McDonald's", "no McDonald's"], header="McDonald's outlets per million population", max_width=200)
map = map.place(legend, align=(1,0), padding=10)

# bar chart
atlas = pd.read_csv("datasets/countries.csv").split_columns('country', "|").split_rows('country').set_index('country')
df2 = df.select(lambda c: c != "Vatican City" and atlas.continent.get(c) == "Europe" or c in ["Georgia", "Azerbaijan", "Armenia"])
df2 = df2.sort_values("permillion", ascending=False)[["permillion"]]
bar = bar_chart(df2, 24, 400, horizontal=True, spacing=1, colors=["#003399"], ymax=df2.iloc[0][0], rlabels=lambda r: Image.from_url_with_cache(atlas.flag[df2.index[r]]).to_rgba().resize((33,22)).pad(1, "grey"), grid_interval=10, clabels=None, label_font=arial(16), ylabel=Image.from_text("McDonald's outlets per million population", arial(16)))

# combine
chart = Image.from_row([map, bar], padding=5, bg="white", yalign=0)
title = Image.from_markup("**EUROPEAN [[McDonald's]] OUTLETS PER CAPITA**", partial(arial, 54), highlight=VegaPalette10.RED)
footer = Image.from_text("* While McDonald's opened their first outlet in Portugal in 1991, they also opened an outlet in Portuguese Macao four years earlier in 1987.", arial(16))
img = Image.from_column([title, chart, footer], bg="white", padding=5)
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/eumcdonalds.png")
