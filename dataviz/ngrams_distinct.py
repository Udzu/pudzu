from pudzu.charts import *
from pudzu.sandbox.bamboo import *

from collections import Counter
import pandas as pd
import numpy as np
import unicodedata
import tqdm


def file_ngrams(filename, n, normalise=str.lower, encoding="utf-8"):
    with open(filename, "r", encoding=encoding) as f:
        counter = Counter()
        for i, line in enumerate(f):
            nline = normalise(line)
            counter.update(nline[j:j+n] for j in range(len(line)-n+1))
            if (i % 100000 == 0):
                print(f"Processed {i} lines")
    return counter


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
    pc = pc[pc.index.map(lambda s: all(unicodedata.category(x).startswith("Ll") for x in s))]
    if accent_strip:
        pc = pc.groupby(pc.index.map(strip_accents)).sum().sort_values(ascending=False)
    pc = pc[pc > 1e-5]
    pc = pc / pc.sum()
    return pc


def distinctive_ngrams(langs, n, accent_strip=False):
    xs = pd.Series(dtype=str)
    pcs = {}
    pc_total = pd.Series(dtype=np.float64)
    for lang in tqdm.tqdm(langs):
        pcs[lang] = make_ngrams(lang, n, accent_strip=accent_strip)
        pc_total = pc_total.add(pcs[lang], fill_value=0)
    pc_total = (pc_total / pc_total.sum()).sort_values(ascending=False)
    if len(langs) == 1:
        # nothing to compare to
        lang, name = first(langs.items())
        xs[name] = pcs[lang].index[0]
    else:
        # better metric?
        for lang, pc in tqdm.tqdm(pcs.items()):
            x = (pc.div(pc_total, fill_value=0) / -np.log(pc)).idxmax()
            #x = pc.sub(pc_total, fill_value=0).idxmax()
            xs[langs[lang]] = x
    return xs


CYRILLIC = {
    "be": "Belarusian", "bg": "Bulgarian", "mk": "Macedonian", "ru": "Russian", "sr": "Serbian", "uk": "Ukrainian"
}

GREEK = {"el": "Greek"}

LATIN = {
    "br": "Breton",
    "ca": "Catalan", "cs": "Czech", "cy": "Welsh",
    "da": "Danish", "de": "German",
    "en": "English", "es": "Spanish", "et": "Estonian", "eu": "Basque",
    "fi": "Finnish", "fo": "Faroese", "fr": "French",
    "ga": "Irish", "gd": "Scottish", "gl": "Galician",
    "hr": "Croatian", "hu": "Hungarian",
    "is": "Icelandic", "it": "Italian",
    "lb": "Luxembourgish", "lt": "Lithuanian", "lv": "Latvian",
    "mt": "Maltese",
    "nl": "Dutch", "no": "Norwegian",
    "pl": "Polish", "pt": "Portuguese",
    "ro": "Romanian",
    "sl": "Slovene", "sk": "Slovak", "sq": "Albanian", "sv": "Swedish",
    "tr": "Turkish",
}

if __name__ == "main":

    dfs = []
    for langs in [LATIN, CYRILLIC, GREEK]:
        df = pd.DataFrame()
        for n in [1,2,3]:
            df[n] = distinctive_ngrams(langs, n, False)
        dfs.append(df)
    df = pd.concat(dfs).sort_index()
    df.loc["Serbo-Croatian"] = [f"{df[n]['Croatian']}\n{df[n]['Serbian']}" for n in [1,2,3]]


    def make_map(df, n):

        def fuzz(c, n):
            return RGBA(c).brighten(random.uniform(-n, n))
            # r,g,b,a = RGBA(c)
            # r,g,b = [clip(x + randint(-n, n), 0, 255) for x in [r,g,b]]
            # return RGBA(r,g,b,a)

        def colorfn(c):
            if c in ['Sea', 'Language Borders']:
                return "white"
            elif c in ['Country Borders']:
                return "#AAAAAA"
            elif c not in df.index:
                return "grey"
            else:
                c = {1: VegaPalette10.GREEN, 2: VegaPalette10.BLUE, 3: VegaPalette10.ORANGE}[n]
                return fuzz(c, 0.1)

        def labelfn(c, w, h):
            if c not in df.index: return None
            label = df[n][c].replace("\\n", "\n")
            return Image.from_text_bounded(label, (w, h), 48, papply(sans, bold=True), line_spacing=5, padding=(0,0,0,2), align="center")

        return map_chart("maps/Eurolang.png", colorfn, labelfn)


    chart = Image.from_row([make_map(df, i) for i in [1,2,3]])
    title = Image.from_column([
    Image.from_text("The most distinctive glyphs, glyph pairs and glyph triplets".upper(), sans(96, bold=True), padding=2),
    Image.from_text("in different European languages, based on comparing each language's Wikipedia to others that use the same script", sans(64), padding=2)],
    bg="white")
    img = Image.from_column([title, chart], bg="white", padding=5)
    img.place(Image.from_text("/u/Udzu", sans(32), fg="black", bg="white", padding=10).pad((2,2,0,0), "black"), align=1, padding=20, copy=False)
    img.resize_fixed_aspect(scale=0.5)
    img.save("output/ngrams.png")
