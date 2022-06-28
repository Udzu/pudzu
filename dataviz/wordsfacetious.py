from pudzu.utils import *
from pudzu.charts import *
from pathlib import Path
import pandas as pd


def aeiou(wiktionary=True):
    file = "Wiktionary" if wiktionary else "Wiki"
    words = pd.Series(Path(f"../corpora/Ranked{file}.txt").read_text().split("\n"))
    words = words.apply(artial(strip_from, "@")).apply(str.lower)

    aeiou = words[words.apply(lambda s: sorted(x for x in s if x in "aeiou") == list("aeiou"))]
    aeiou_ns = aeiou[~aeiou.str.contains(" ")]
    aeiou.name = "all"
    aeiou_ns.name = "ns"

    best = aeiou.groupby(lambda s: "".join(x for x in aeiou[s] if x in "aeiou")).first()
    best_ns = aeiou_ns.groupby(lambda s: "".join(x for x in aeiou_ns[s] if x in "aeiou")).first()
    df = pd.concat([best, best_ns], axis=1)

    return df


df = pd.read_csv("datasets/wordsfacetious.csv", index_col=0)
grid = list(generate_batches(df.to_dict()["word"].items(), 24))
cols = []
for words in grid:
    col = Image.from_column([
        Image.from_markup(f"//{k}//: {v}", partial(arial, 24), beard_line=True)
        for k,v in words
    ], xalign=0)
    cols.append(col)

chart = Image.from_row(cols, bg="white", padding=20)
title = Image.from_text_bounded("lexical items containing all 5 vowels once".upper(), chart.size, 60, partial(arial, bold=True))
img = Image.from_column([title, chart], padding=10, bg="white")
img.save("output/wordsfacetious.png")
