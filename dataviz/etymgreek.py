from pudzu.charts import *
from pudzu.sandbox.bamboo import *
from graphviz import Digraph

df = pd.read_csv("datasets/etymgreek.csv").sort_values("language").set_index("language")
flags = pd.read_csv("datasets/countries.csv").split_columns('country', "|").explode('country').set_index('country')['flag']

g = Digraph('G', filename='cache/etymgreek.gv', format="png")
g.attr(newrank="True")

default_img = "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b0/No_flag.svg/1024px-No_flag.svg.png"

def make_flag(language):
    url = get_non(df.flag, language, default_img)
    if not url.startswith("http"): url = flags[url]
    icon = Image.from_url_with_cache(url).to_rgba().resize((160,100)).pad(1 if language != "Nepal" else 0, "grey")
    label = Image.from_text(language, sans(20), align="center")
    flag = Image.from_column([icon, label], padding=2)
    flag.save(f"cache/icons/{language}.png")

for language, row in df.iterrows():
    make_flag(language)
    g.node(language, image=f"icons/{language}.png", shape="none", label="")
    if get_non(df.greek, language):
        for to in row.greek.split("|"):
            g.edge(language, to, label="           ")

g.render()

i = Image.open("cache/etymgreek.gv.png")

title = Image.from_text("Directed graph of stereotypical incomprehensibility".upper(), sans(120, bold=True))
subtitle = Image.from_text("languages mentioned in the most common translation of the 'it's all Greek to me' idiom", sans(80, italics=True), padding=(0,0,0,20))
footer = Image.from_markup("Inspired by [[https:/\/languagelog.ldc.upenn.edu/nll/?p=1024]]. Sources: Wikipedia, Omniglot, Google and reddit.", partial(sans, 36), padding=10)

img = Image.from_column([title, subtitle, i, footer], padding=10, bg="white")
img.place(Image.from_text("/u/Udzu", sans(48), padding=10).pad((2,2,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/etymgreek.png")

