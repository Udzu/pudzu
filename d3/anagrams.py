import string
from pathlib import Path
from generate import *
from pudzu.charts import *
from pudzu.sandbox.bamboo import *

# def sort(w):
#     return "".join(sorted(c for c in w if c in string.ascii_letters))
# def read_dict(name):
#     s = Path(name).read_text().lower().split("\n")
#     d = {}
#     for w in s:
#         d.setdefault(sort(w), []).append(w)
#     return d
#
# sowpods = read_dict("../corpora/sowpods.txt")
# twl = read_dict("../corpora/twl06.txt")
#
# df = pd.read_csv("datasets/countries.csv").split_columns("country", "|").explode("country")
# cs = set(df.country)
# cs.add("Bahamas")
# cs.add("Gambia")
# cs.add("Vatcian")
#
# for c in sorted(cs):
#     s = sowpods.get(sort(c.lower()))
#     t = twl.get(sort(c.lower()))
#     if s or t:
#         print(c, s, t)




df = pd.read_csv("datasets/anagrams.csv")

PALETTE = { "c": VegaPalette10.PURPLE,
            "a": VegaPalette10.BLUE,
            "sc": VegaPalette10.PINK,
            "sa": VegaPalette10.LIGHTBLUE
}

PATTERNS = ""
WIDTH = 10

for p in ["sc|a"]:
    if isinstance(p, str) and p not in PALETTE:
        ps = p.split("|")
        if all(p in PALETTE for p in ps):
            rects = [f'<rect x="{i*WIDTH}" y="0" width="{WIDTH}" height="{WIDTH*len(ps)}" style="fill:{PALETTE[p].to_hex()}"/>' for i,p in enumerate(ps)]
            PATTERNS += f'''<defs>
  <pattern id="{''.join(ps)}" width="{WIDTH*len(ps)}" height="{WIDTH*len(ps)}" patternTransform="rotate(45 0 0)" patternUnits="userSpaceOnUse">
    {'  '.join(rects)}
  </pattern>
</dev>
'''
            PALETTE[p] = f'url(#{"".join(ps)})'
        else: print(ps)


def colorfn(c, w):
    c = c.lower()
    if c == w: return "c"
    elif c+"+" == w: return "sc"
    elif w.endswith("+"): return "sa"
    elif "/" in w: return "sc|a"
    else: return "a"

def labelfn(c, w):
    w = strip_to(w.strip("+"), "/")
    if c in ["Congo", "Jordan"]: return " "
    return w

labels = { r.country: labelfn(r.country, r.word) for _,r in df.iterrows() }
colormap = { r.country: colorfn(r.country, r.word) for _,r in df.iterrows() }

CODES = pd.Series(atlas.code.index.values, index=atlas.code )
LABELS = { code: labels.get(country, " ") for code, country in CODES.items() }
for code, country in CODES.items():
    if labels.get(country): LABELS[code] = labels.get(country)
for C in ["BES", "BVT", "UMI", "HMD", "northern_cyprus", "somaliland", "kosovo"]: LABELS[C] = " "

generate_datamap("anagrams", colormap, palette=PALETTE, patterns=PATTERNS, codifier=partial(codify_countries, dependencies=True), labels=LABELS, label_size=12)

chart = Image.open("temp/anagrams.png")
legend = generate_legend(
  [PALETTE[x] for x in ["c", "sc", "a", "sa"]],
  ["Country name is a word in both SOWPODS and TWL",
   "Country name is a word only in SOWPODS",
  "Country name has an anagram in both SOWPODS and TWL",
   "Country name has an anagram only in SOWPODS"
  ], 40, partial(arial, 16), header="Country names that can be played in Scrabble:")
chart = chart.place(legend, align=(0,1), padding=100)

surtitle = Image.from_markup("**COUNTRY NAMES PLAYABLE IN SCRABBLE** as words or in anagrams", partial(arial, 60))
subtitle = Image.from_markup("//using the American TWL or international SOWPODS Scrabble word lists//", partial(arial, 36))
title = Image.from_column([surtitle, subtitle])
img = Image.from_column([title, chart], bg="white", padding=5)
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/anagrams.png")
