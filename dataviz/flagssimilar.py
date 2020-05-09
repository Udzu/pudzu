from pudzu.charts import *
from pudzu.sandbox.bamboo import *
from graphviz import Digraph

df = pd.read_csv("datasets/flagssimilar.csv")
flags = pd.read_csv("datasets/countries.csv").split_columns('country', "|").explode('country').set_index('country')['flag']

g = Digraph('G', filename='cache/flagssimilar.gv', format="png")
g.attr(rankdir='LR')

def make_flag(country):
    icon = Image.from_url_with_cache(flags[country]).to_rgba().resize_fixed_aspect(width=160).pad(1 if country != "Nepal" else 0, "grey")
    label = Image.from_text(start.replace("the G", "\nthe G").replace("can Re","can\nRe").replace("and P","\nand P"), sans(20), align="center")
    flag = Image.from_column([icon, label], padding=2)
    flag.save(f"cache/icons/{country}.png")

for _, (start, end) in reversed(list(df.iterrows())):
    make_flag(start)
    g.node(start, image=f"icons/{start}.png", shape="none", label="")
    g.edge(start, end)
    
g.render()
graph = Image.open("cache/flagssimilar.gv.png")

def split(img, offsets):
    print(offsets)
    y = 0
    slices = []
    for i,o in enumerate(offsets):
        slices.append(img.crop((0,y,img.width-(180)*(i!=1),y+o)))
        y += o
    slices.append(img.crop((0,y,img.width,img.height)))
    return Image.from_row(slices, yalign=0, padding=30, bg="white")
    
i = split(graph, [3370, 3310, 3350])

title = Image.from_text_justified("The most similar flag".upper(), int(i.width * 0.7), 240, partial(sans, bold=True))
subtitle = Image.from_text_justified("to the flags of each of the 195 UN member and observer states", int(i.width * 0.67), 240, partial(sans, italics=True), padding=(0,0,0,20))
img = Image.from_column([title, subtitle, i], padding=10, bg="white")
img.place(Image.from_text("/u/Udzu", sans(48), padding=10).pad((2,2,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/flagssimilar.png")
img.resize_fixed_aspect(scale=0.5).save("output/flagssimilar2.png")

