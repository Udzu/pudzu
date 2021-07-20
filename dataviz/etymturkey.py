from pudzu.charts import *
from pudzu.sandbox.bamboo import *
from graphviz import Digraph

df = pd.read_csv("datasets/etymturkey.csv").sort_values("language").set_index("language")
flags = pd.read_csv("datasets/countries.csv").split_columns('country', "|").explode('country').set_index('country')['flag']

g = Digraph('G', filename='cache/etymturkey.gv', format="png")
g.attr(newrank="True")

default_img = "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b0/No_flag.svg/1024px-No_flag.svg.png"

def make_flag(language):
    url = get_non(df.flag, language, language)
    if not url.startswith("http"): url = flags[url]
    icon = Image.from_url_with_cache(url).to_rgba().resize((160,100)).pad(1 if language != "Nepal" else 0, "grey")
    label = Image.from_text(language, sans(20), align="center")
    flag = Image.from_column([icon, label], padding=2)
    flag.save(f"cache/icons/{language}.png")

for language, row in df.iterrows():
    make_flag(language)
    g.node(language, image=f"icons/{language}.png", shape="none", label="")
    if get_non(df.country, language):
        for to, label in zip(row.country.split("|"), row.word.split("|")):
            label = label.replace(r"\n", r" \n ")
            g.edge(language, to, label=f" {label} ")

g.render()

i = Image.open("cache/etymturkey.gv.png")
t = Image.from_url_with_cache("https://images.unsplash.com/photo-1606024496931-5376c8ffbe88?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=658&q=80").resize_fixed_aspect(height=i.height)
i = Image.from_row([i,t], padding=20)

title = Image.from_text("Where do turkeys come from?".upper(), sans(112, bold=True))
subtitle = Image.from_text("countries that the North American bird is named after in different languages", sans(56, italics=True), padding=(0,0,0,20))

img = Image.from_column([title, subtitle, i], padding=10, bg="white")
#img.place(Image.from_text("/u/Udzu", sans(48), padding=10).pad((2,2,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/etymturkey.png")

