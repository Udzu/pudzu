from pudzu.charts import *
from pudzu.sandbox.bamboo import *
from ngrams_distinct import file_ngrams, LATIN, CYRILLIC

from graphviz import Digraph
import numpy as np
import tqdm


def make_ngrams(lang, n, accent_strip=False):
    try:
        pc = pd.read_csv(f"../corpora/wikis/{lang}-{n}grams.csv", index_col=0).n
    except FileNotFoundError:
        ngrams = file_ngrams(f"../corpora/wikis/{lang}wiki.txt", n)
        df = pd.DataFrame.from_dict(ngrams, orient="index", columns=["n"]).sort_values("n", ascending=False)
        df = df[~df.index.str.contains(" ")]
        pc = df.n / df.n.sum()
        pc.to_csv(f"../corpora/wikis/{lang}-{n}grams.csv")
    pc = pc[pc.index.dropna()]
    pc = pc[pc > 1e-7]
    if accent_strip:
        pc = pc.groupby(pc.index.map(strip_accents)).sum().sort_values(ascending=False)
    pc = pc / pc.sum()
    return pc


def similar_ngrams(langs, n, accent_strip=False):
    pcs = {}
    grid = {}
    for lang in tqdm.tqdm(langs):
        pcs[lang] = make_ngrams(lang, n, accent_strip=accent_strip)
    for lang1 in tqdm.tqdm(langs):
        for lang2 in tqdm.tqdm(langs):
            if lang1 == lang2: continue
            s = np.abs(pcs[lang1].sub(pcs[lang2], fill_value=0)).sum()
            # s = np.square(np.sqrt(pcs[lang1]).sub(np.sqrt(pcs[lang2]), fill_value=0)).sum()
            grid.setdefault(langs[lang1], {})[langs[lang2]] = s #-math.log(s)
    return grid


LATIN=dict(LATIN, eo="Esperanto", fy="Frisian")
N = 3

l = similar_ngrams(LATIN, N)
c = similar_ngrams(CYRILLIC, N)

flags = pd.read_csv("datasets/countries.csv").split_columns('country', "|").explode('country').set_index('country')['flag']
default_img = "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b0/No_flag.svg/1024px-No_flag.svg.png"


def make_flag(language, country):
    url = flags.get(country, country)
    if not url.startswith("http"): url = default_img
    icon = Image.from_url_with_cache(url).to_rgba().resize((160,100)).pad(1 if language != "Nepal" else 0, "grey")
    label = Image.from_text(language.replace("Scottish", "Scottish Gaelic").replace("Norwegian", "Norwegian (Bokmål)"), sans(20), align="center")
    flag = Image.from_column([icon, label], padding=2)
    flag.save(f"cache/icons/{language}.png")


g = Digraph('G', filename='cache/ngrams.gv', format="png")
g.attr(newrank="True")
pairs = list(sorted(c.items())) + list(l.items())
for language, targets in reversed(pairs):

    FLAGS = {
        "English": "UK", #"https://upload.wikimedia.org/wikipedia/en/thumb/b/be/Flag_of_England.svg/1920px-Flag_of_England.svg.png",
        "Danish": "Denmark", "Polish": "Poland", "Slovak": "Slovakia", "Finnish": "Finland",
        "French": "France", "Spanish": "Spain", "Dutch": "Netherlands", "Irish": "Ireland",
        "Catalan": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/ce/Flag_of_Catalonia.svg/1280px-Flag_of_Catalonia.svg.png",
        "Welsh": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dc/Flag_of_Wales.svg/1920px-Flag_of_Wales.svg.png",
        "Breton": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7d/Flag_of_Brittany.svg/1280px-Flag_of_Brittany.svg.png",
        "Scottish": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/Flag_of_Scotland.svg/1920px-Flag_of_Scotland.svg.png",
        "Basque": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2d/Flag_of_the_Basque_Country.svg/1920px-Flag_of_the_Basque_Country.svg.png",
        "Galician": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/64/Flag_of_Galicia.svg/1280px-Flag_of_Galicia.svg.png",
        "Esperanto": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f5/Flag_of_Esperanto.svg/1024px-Flag_of_Esperanto.svg.png",
        "Frisian": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/ca/Frisian_flag.svg/1280px-Frisian_flag.svg.png",
    }
    matches = [x for x in flags.index if x.startswith(language[:4])]
    if len(matches) == 1 or language in ["Russian", "Czech", "Slovene", "Turkish"]:
        country = matches[-1]
    else:
        country = FLAGS[language]
    make_flag(language, country)

    target, score = min(targets.items(), key=lambda kv: kv[1])
    g.node(language, image=f"icons/{language}.png", shape="none", label="")
    g.edge(language, target) #, label=f"{score:.0%}")

make_flag("Greek", "Greece")
g.node("Greek", image=f"icons/Greek.png", shape="none", label="")
g.render()

i = Image.open("cache/ngrams.gv.png")

title = Image.from_text("Most ‘visually similar’ language to each european language".upper(), sans(92, bold=True))
subtype = {1: "", 2: " pair", 3: " triplet"}[N]
subtitle = Image.from_text(f"where similarity is based on the closeness of the languages’ letter{subtype} distributions (measured using their respective Wikipedias)", sans(52, italics=True), padding=(0,0,0,20))

img = Image.from_column([title, subtitle, i], padding=15, bg="white")
img.place(Image.from_text("/u/Udzu", sans(24), padding=10).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save(f"output/ngrams_similar_{N}.png")

