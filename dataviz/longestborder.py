from pudzu.charts import *
from pudzu.sandbox.bamboo import *
from graphviz import Digraph

df = pd.read_csv("datasets/longestborder.csv")
df = df[~df.other.isna()]

flags = pd.read_csv("datasets/countries.csv").split_columns('country', "|").explode('country').set_index('country')['flag']
flags["Afghanistan"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Flag_of_the_Taliban.svg/1280px-Flag_of_the_Taliban.svg.png"

g = Digraph('G', filename='cache/longestborder.gv', format="png")
g.attr(rankdir='LR')

MILES = True

def make_flag(country):
    print(country)
    icon = Image.from_url_with_cache(flags[country]).to_rgba().resize_fixed_aspect(width=160).pad(1 if country != "Nepal" else 0, "grey")
    label = Image.from_text(start.replace("the G", "\nthe G").replace("can Re","can\nRe").replace("and P","\nand P"), sans(20), align="center")
    flag = Image.from_column([icon, label], padding=2)
    flag.save(f"cache/icons/{country}.png")

seen = set()
for _, (start, end, km) in reversed(list(df.iterrows())):
    make_flag(start)
    g.node(start, image=f"icons/{start}.png", shape="none", label="")
    if (end, start) in seen:
        pass
    else:
        seen.add((start, end))
        if len(df[(df.country == end) & (df.other == start)]):
            g.edge(start, end, label=f"{int(km):,} km", dir="both")
        else:
            g.edge(start, end, label=f"{int(km):,} km")

    
g.render()
graph = Image.open("cache/longestborder.gv.png")

def split(img, offsets):
    y = 0
    slices = []
    for i,o in enumerate(offsets):
        slices.append(img.crop((0,y,img.width-(180)*(i==0)-(150)*(i<2),y+o)))
        y += o
    if img.height > y:
        slices.append(img.crop((0,y,img.width,img.height)))
    return Image.from_row(slices, yalign=0.2, padding=30, bg="white")
    
i = split(graph, [3690, 3540])
#i = graph

title = Image.from_text("Longest land border".upper(), sans(280, bold=True))
subtitle = Image.from_text("of each of the 157 widely recognised states with land borders", sans(128, italics=True), padding=(0,0,0,20))
subsubtitle = Image.from_text("(an arrow from country A to country B means that A's longest land border is with B)", sans(64), fg="#555555", padding=(0,0,0,20))

img = Image.from_column([title, subtitle, subsubtitle, i], padding=10, bg="white")
img.place(Image.from_text("/u/Udzu", sans(48), padding=10).pad((2,2,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/longestborder.png")
img.resize_fixed_aspect(scale=0.5).save("output/longestborder2.png")

