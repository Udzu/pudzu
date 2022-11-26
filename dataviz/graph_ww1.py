from pudzu.charts import *
from pudzu.sandbox.bamboo import *
from ngrams_distinct import file_ngrams, LATIN, CYRILLIC

from graphviz import Digraph
import numpy as np
import tqdm
import seaborn as sns

df = pd.read_csv("datasets/graph_ww1.csv")

flags = pd.read_csv("datasets/countries.csv").split_columns('country', "|").explode('country').set_index('country')['flag']
default_img = "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b0/No_flag.svg/1024px-No_flag.svg.png"
flags["Austria-Hungary"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7a/Flag_of_the_Habsburg_Monarchy.svg/1024px-Flag_of_the_Habsburg_Monarchy.svg.png"
flags["Montenegro"] = "https://upload.wikimedia.org/wikipedia/commons/c/c2/Kingdom_of_Montenegro_Flag_1905-1918.png"
flags["Serbia"] = "https://upload.wikimedia.org/wikipedia/commons/e/e6/Flag_of_Kingdom_of_Serbia_from_1882-1918.png"
flags["Germany"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1f/Flag_of_Germany_%281867%E2%80%931918%29.svg/1920px-Flag_of_Germany_%281867%E2%80%931918%29.svg.png"
flags["Ottoman Empire"] = flags["Turkey"]
flags["Italy"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0d/Flag_of_Italy_%281861-1946%29_crowned.svg/1920px-Flag_of_Italy_%281861-1946%29_crowned.svg.png"
flags["Greece"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/State_Flag_of_Greece_%281863-1924_and_1935-1973%29.svg/1920px-State_Flag_of_Greece_%281863-1924_and_1935-1973%29.svg.png"
flags["Siam"] = flags["Thailand"]
flags["China"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/f/ff/Flag_of_China_%281912%E2%80%931928%29.svg/1920px-Flag_of_China_%281912%E2%80%931928%29.svg.png"
flags["Costa Rica"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/db/State_Flag_of_Costa_Rica_%281906-1964%29.svg/1920px-State_Flag_of_Costa_Rica_%281906-1964%29.svg.png"
flags["Nicaragua"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/1/13/Flag_of_Nicaragua_%281908%E2%80%931971%29.svg/1920px-Flag_of_Nicaragua_%281908%E2%80%931971%29.svg.png"
flags["USA"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f5/Flag_of_the_United_States_%281912-1959%29.svg/1920px-Flag_of_the_United_States_%281912-1959%29.svg.png"

def make_flag(country):
    url = flags.get(country, country)
    if not url.startswith("http"): url = default_img
    icon = Image.from_url_with_cache(url).to_rgba().resize((160,100)).pad(1, "grey")
    label = Image.from_text(country.replace("UK", "British Empire"), sans(20), align="center")
    flag = Image.from_column([icon, label], padding=2)
    flag.save(f"cache/icons/{country}.png")


g = Digraph('G', filename='cache/graph_ww1.gv', format="png")
g.attr(newrank="True")
#g.attr(newrank="True", rankdir="LR", ranksep="15", splines="False")

blues = list(reversed(
"""#bdbdbd
#969696
#737373
#525252
#252525""".split("\n")))

COUNTRIES = set()
BAD = {"Austria-Hungary", "Bulgaria", "Ottoman Empire", "Germany"}


for _, row in sorted(df.iterrows(), key=lambda r: (r[1].date[-1], r[1].source, r[1].target), reverse=False):
    COUNTRIES.add(row.source)
    COUNTRIES.add(row.target)
    make_flag(row.source)
    make_flag(row.target)
    g.node(row.source, image=f"icons/{row.source}.png", shape="none", label="")
    g.node(row.target, image=f"icons/{row.target}.png", shape="none", label="")
    c = blues[int(row.date[-1])-4]
    d = row.date.replace(" 19","<br/>19")
    w = "3.5" if "Jul 1914" in row.date else "2.5" if "Aug 1914" in row.date else "2" if "1914" in row.date else "1.5"
    g.edge(row.source, row.target, color=c, label=f'<<font color="{c}">{d}</font>>', penwidth=w)

# bad = Digraph('B')
# bad.attr(rank="same")
# good = Digraph('G')
# good.attr(rank="same")
# for country in BAD:
#     bad.node(country)
# for country in COUNTRIES - BAD:
#     good.node(country)
# g.subgraph(bad)
# g.subgraph(good)

g.render()

i = Image.open("cache/graph_ww1.gv.png")
u = Image.from_url_with_cache("https://i.imgur.com/7AHQlZK.jpeg")
i = Image.from_row([i, u], padding=10)

title = Image.from_text("Declarations of war during World War I".upper(), sans(172, bold=True), padding=20)

img = Image.from_column([title, i], padding=15, bg="white")
img.place(Image.from_text("/u/Udzu", sans(24), padding=10).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/graph_ww1.png")

img.resize_fixed_aspect(scale=0.75).save("output/graph_ww1c.png")