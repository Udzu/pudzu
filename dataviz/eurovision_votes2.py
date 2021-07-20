from pudzu.charts import *
from pudzu.sandbox.bamboo import *
from graphviz import Digraph

df = pd.read_csv("datasets/eurovision_votes.csv")
flags = pd.read_csv("datasets/countries.csv").split_columns('country', "|").explode('country').set_index('country')['flag']

g = Digraph('G', filename='cache/flagseurovision.gv', format="png")
g.attr(rankdir='LR', newrank="True")

def make_flag(country):
    icon = Image.from_url_with_cache(flags[country]).to_rgba().resize_fixed_aspect(height=120).pad(1 if country != "Nepal" else 0, "grey")
    label = Image.from_text(country, sans(20), align="center")
    flag = Image.from_column([icon, label], padding=2)
    flag.save(f"cache/icons/{country}.png")

for _, row in df.iterrows():
    make_flag(row.country)
    g.node(row.country, image=f"icons/{row.country}.png", shape="none", label="")
    g.edge(row.country, row.to, label=str(row.to_score), penwidth=str((row.to_score-5)/1.5))    
#    g.edge(row["from"], row.country, label=str(row.from_score), penwidth=str((row.to_score-5)/2), color="#660000", fontcolor="#660000")    

g.render()


graph = Image.open("cache/flagseurovision.gimp.png")


title = Image.from_text_justified("Eurovision friendship clusters: 1975–2017".upper(), int(graph.width * 0.7), 240, partial(sans, bold=True))
subtitle = Image.from_markup_bounded("//highest average points given by each country [source: [[escstats.com]]]; excludes ex-countries and those with <3 appearances//", (int(graph.width * 0.67), 200), 120, partial(partial, sans), padding=(0,0,0,20))
img = Image.from_column([title, subtitle, graph], padding=10, bg="white")
img.place(Image.from_text("/u/Udzu", sans(48), padding=10).pad((2,2,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/flagseurovision.png")
img.resize_fixed_aspect(scale=0.5).save("output/flagseurovision2.png")

