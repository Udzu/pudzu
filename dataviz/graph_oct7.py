from pudzu.charts import *
from pudzu.sandbox.bamboo import *
from ngrams_distinct import file_ngrams, LATIN, CYRILLIC

from graphviz import Digraph
import numpy as np
import tqdm
import seaborn as sns

df = pd.read_csv("datasets/graph_oct7.csv").fillna("forward")

flags = pd.read_csv("datasets/countries.csv").split_columns('country', "|").explode('country').set_index('country')['flag']
default_img = "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b0/No_flag.svg/1024px-No_flag.svg.png"

def make_flag(country):
    url = flags.get(country, country)
    if not url.startswith("http"): url = default_img
    icon = Image.from_url_with_cache(url).to_rgba().resize((160,100)).pad(1, "grey")
    label = Image.from_text(country, sans(20), align="center")
    flag = Image.from_column([icon, label], padding=2)
    flag.save(f"cache/icons/{country}.png")


g = Digraph('G', filename='cache/graph_oct7.gv', format="png")
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


for _, row in sorted(df.iterrows(), key=lambda r: (r[1].source, r[1].target), reverse=False):
    COUNTRIES.add(row.source)
    COUNTRIES.add(row.target)
    make_flag(row.source)
    make_flag(row.target)
    g.node(row.source, image=f"icons/{row.source}.png", shape="none", label="")
    g.node(row.target, image=f"icons/{row.target}.png", shape="none", label="")
    g.edge(row.source, row.target, dir=row.dir)

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

i = Image.open("cache/graph_oct7.gv.png")

# first from each
# 7 October: Hamas fires missiles into Israel; Israeli Air Foce attacks Gaza.
# 8 October: Hezbollah fires missiles into Israel; Israel fires back.
# 12 October: Israel attacks on Syrian airports; Syria fires mortars in return.
# 20 December: Syrian rockets fired at Golan Heights

# u = Image.from_url_with_cache("https://i.imgur.com/7AHQlZK.jpeg")
# i = Image.from_row([i, u], padding=10)
#
title = Image.from_text("air and missile attacks since Oct 7".upper(), sans(44, bold=True), padding=(0,20,0,0))
subtitle = Image.from_markup("//source//: [[https:\//en.wikipedia.org/wiki/Timeline_of_the_2023_Israel%E2%80%93Hamas_war]] //et al.//", partial(sans, 20), padding=(0,0,0,20))

img = Image.from_column([title, subtitle, i], padding=15, bg="white")
img.place(Image.from_text("/u/Udzu", sans(24), padding=10).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/graph_oct7.png")
#
# img.resize_fixed_aspect(scale=0.75).save("output/graph_ww1c.png")