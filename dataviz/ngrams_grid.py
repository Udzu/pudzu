import subprocess
from collections import ChainMap
from pathlib import Path
from string import ascii_lowercase as ascii

import hangul_jamo
import seaborn as sns
from tqdm import tqdm

from ngrams_distinct import file_ngrams, LATIN, CYRILLIC, GREEK
from pudzu.charts import *
from math import log

def extract_wikidump(lang):
    bz2 = list(Path("../corpora/wikis/").glob(f"{lang}*.bz2"))
    assert len(bz2) == 1
    cmd = ['wikiextractor', '-b', '500M', '--no-templates', '-o', 'wikitmp', str(bz2[0])]
    subprocess.run(cmd).check_returncode()
    os.system(r"tr < wikitmp/AA/wiki_00 -d '\000' > wikitmp/AA/wiki_00.a")
    os.system('rg -v "</?doc" wikitmp/AA/wiki_00.a > wikitmp/AA/wiki_00.b')
    os.system(f'rg -v -U "\n.*\n\n\n" wikitmp/AA/wiki_00.b > ../corpora/wikis/{lang}wiki.txt')
    subprocess.run(["rm", "-rf", "wikitmp"])

def convert_size(size_bytes):
   if size_bytes == 0:
       return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   if size_bytes / p > 1000:
       i += 1
       s = 1
   else:
       s = int(round_significant(size_bytes / p, 2))
   return "%s %s" % (s, size_name[i])

def partial_strip(xs, ignore=""):
    return "".join(
        c for x in xs for c in (unicodedata.normalize("NFD", x) if x not in ignore else (x,)) if not unicodedata.combining(c)
    )

def fold_char(x):
    # if unicodedata.category(x)[0] == "P":
    #     return "@"
    return {
        "ς": "σ",
        "ך": "כ",
        "ם": "מ",
        "ן": "נ",
        "ף": "פ",
        "ץ": "צ",
    }.get(x, x)

def fold_vietnamese(xs):
    xs = unicodedata.normalize("NFD", xs)
    xs = strip_any(xs, "\N{COMBINING DOT BELOW}\N{COMBINING GRAVE ACCENT}\N{COMBINING ACUTE ACCENT}\N{COMBINING HOOK ABOVE}\N{COMBINING TILDE}")
    xs = unicodedata.normalize("NFC", xs)
    return xs

FOLDER = {"vi": fold_vietnamese}

def lower_turkish(xs):
    return xs.replace("I", "ı").replace("İ", "i").lower()

NORMALISER = {"tr": lower_turkish, "ko": hangul_jamo.decompose}

def make_ngrams(lang, n, letters, fold_chars=True, strip_accents=True, filter_accents=False, percent=True):
    try:
        pc = pd.read_csv(f"../corpora/wikis/{lang}-{n}grams.csv", index_col=0).n
    except FileNotFoundError:
        ngrams = file_ngrams(f"../corpora/wikis/{lang}wiki.txt", n, normalise=NORMALISER.get(lang, str.lower))
        pc = pd.DataFrame.from_dict(ngrams, orient="index", columns=["n"]).sort_values("n", ascending=False).n
        pc.to_csv(f"../corpora/wikis/{lang}-{n}grams.csv")
    pc = pc[pc.index.dropna()]
    if fold_chars:
        pc = pc.groupby(pc.index.map(lambda xs: "".join(map(FOLDER.get(lang, fold_char), xs)))).sum()
    if strip_accents:
        pc = pc.groupby(pc.index.map(lambda xs: partial_strip(xs, letters))).sum()
    pc = pc[pc.index.map(lambda s: len(s) == n and all(x in letters for x in (partial_strip(s, letters) if filter_accents else s)))].sort_values(ascending=False)
    if percent:
        pc = pc / pc.sum()
    return pc

def strip_punctuation(s):
    start, end = 0, 0
    for start in range(len(s)):
        if not unicodedata.category(s[start]).startswith("P"):
            break
    for end in reversed(range(len(s))):
        if not unicodedata.category(s[end]).startswith("P"):
            break
    return s[start:end+1]

def make_wordlist(lang):
    try:
        pc = pd.read_csv(f"../corpora/wikis/{lang}-words.csv", index_col=0).n
    except FileNotFoundError:
        with open(f"../corpora/wikis/{lang}wiki.txt", "r", encoding="utf-8") as f:
            counter = Counter()
            for i,l in enumerate(f):
                counter.update(l.rstrip().lower().split(" "))
                if (i % 100000 == 0):
                    print(f"Processed {i} lines")
        pc = pd.DataFrame.from_dict(counter, orient="index", columns=["n"]).n
        pc = pc.groupby(pc.index.map(strip_punctuation)).sum().sort_values(ascending=False)
        pc.to_csv(f"../corpora/wikis/{lang}-words.csv")
    pc = pc[pc.index.dropna()]
    return pc

def make_topwords(lang, letters):
    try:
        tw = pd.read_csv(f"../corpora/wikis/{lang}-topwords.csv", index_col=0)
    except FileNotFoundError:
        logger.info(f"Generating {lang} top words")
        pc = make_wordlist(lang)
        pc = pc / pc.sum()
        gb = pc.groupby(pc.index.map(lambda s: partial_strip(
            (
                fold_vietnamese(s) if lang=="vi" else hangul_jamo.decompose(s) if lang == "ko" else s
            ), letters)[0:1]))
        d = {c: [matches.index[0], matches[0]] for c in tqdm(letters)
             for matches in [gb.get_group(c) if c in gb.groups else []]
             if len(matches) > 0}
        tw = pd.DataFrame.from_dict(d, orient="index", columns=["word", "pc"])
        tw.to_csv(f"../corpora/wikis/{lang}-topwords.csv")
    if lang == "ko":
        tw = tw[~tw.word.map(lambda s: hangul_jamo.is_jamo_character(s[0]))]
    return tw


def render_words(lang, letters, n, min=3, max=10, save=True, overwrite=False):
    path = Path(f"../corpora/wikis/{lang}-markov{n}.txt")
    try:
        if overwrite:
            raise FileNotFoundError
        words = path.read_text().split()
    except FileNotFoundError:
        trigrams = make_ngrams(lang, 3, letters, percent=False, strip_accents=False, filter_accents=True, fold_chars=False)
        gb = trigrams.groupby(trigrams.index.map(lambda s: s[:2]))
        bigrams = Counter(gb.sum().to_dict())
        wordlist = make_wordlist(lang)
        words = []
        while len(words) < n:
            ngram = bigrams.random_choice(filter=lambda n: n[0] == " ")
            output = ngram
            while True:
                if len(output) > 0 and output[-1] == " ":
                    output = output.strip()
                    if lang=="vi": max = 5
                    if (min <= len(output) <= max) and wordlist.get(output, 0) <= 10:
                        if lang=="ko":
                            output = hangul_jamo.compose(output)
                        words.append(output)
                    break
                elif ngram in bigrams:
                    v = Counter(gb.get_group(ngram).to_dict()).random_choice()
                    output += v[-1]
                    ngram = v[1:]
        words = sorted(words)
        if save:
            path.write_text("\n".join(words), encoding="utf-8")
    return words


# Grid chart
LATIN["uk"] = "Ukrainian"
LATIN["id"] = "Indonesian"
LATIN["vi"] = "Vietnamese"
LATIN["sw"] = "Swahili"
LATIN["sco"] = "Scots"
LATIN["haw"] = "Hawaiian"
NAMES = ChainMap(LATIN, CYRILLIC, GREEK, {"he": "Hebrew", "ko": "Korean"})

def main(lang, letters, notes=None, suffix=""):
    FONT = sans
    UFONT = FONT if lang != "ko" else font_family("fonts/Arial-Unicode")
    NAME = NAMES[lang]
    TITLE = f"Letter and next-letter frequencies in {NAME}".upper()
    SIZE = convert_size(Path(f"../corpora/wikis/{lang}wiki.txt").stat().st_size)
    SUBTITLE = f"measured across {SIZE} of article text from Wikipedia"
    NOTE = (" " + notes) if notes else ""

    SCALE = 1
    BOX_SIZE = 40 * SCALE

    logger.info(f"Generating {NAME} grid chart")
    index = make_ngrams(lang, 1, letters)
    bigrams = make_ngrams(lang, 2, letters)
    trigrams = make_ngrams(lang, 3, letters)
    topwords = make_topwords(lang, letters)
    gb = bigrams.groupby(bigrams.index.map(lambda s: s[0]))
    grid = []
    for x in index.index:
        row = gb.get_group(x).sort_values(ascending=False)
        row = row / row.sum()
        row.index = row.index.map(lambda s: s[-1])
        grid.append(list(row.items()))
    data = pd.DataFrame(grid, index=list(index.items()))

    pone = tmap(RGBA, sns.color_palette("Reds", 8))
    ptwo = tmap(RGBA, sns.color_palette("Blues", 8))
    pthree = tmap(RGBA, sns.color_palette("Greys", 8))
    color_index = lambda p: 0 if p == 0 else clip(6 + int(log(p, 10) * 2), 0, 6)

    def image_fn(pair, palette, row=None, size=BOX_SIZE):
        if pair is None: return None
        bg = palette[color_index(pair[1])]
        img = Image.new("RGBA", (size, size), bg)
        img.place(Image.from_text(pair[0], UFONT(size // 2), "black", bg=bg), copy=False)
        if row is not None and pair[0] != " ":
            if not isinstance(row, str):
                tris = trigrams[trigrams.index.str.startswith(index.index[row] + pair[0])]
                row = " " if tris.empty else tris.idxmax()[-1]
            img.place(Image.from_text(row, UFONT(round(size / 3.5)), "black", bg=bg), align=(1, 0),
                      padding=(size // 8, size // 5), copy=False)
        return img

    def topword_fn(pair, palette, size=BOX_SIZE):
        if pair[0] not in topwords.index: return None
        tw = topwords.loc[pair[0]]
        bg = palette[color_index(tw.pc)]
        img = Image.new("RGBA", (size*3, size), bg)
        img.place(
            Image.from_text_bounded(tw.word, (size*3, size), (size // 2), UFONT, fg="black", bg=bg, padding=(5,0)),
            copy=False)
        return img

    grid = grid_chart(data, lambda p, r: image_fn(p, row=r, palette=ptwo), fg="black", bg="white", padding=round(SCALE),
                      row_label= {
                          GridChartLabelPosition.LEFT: lambda i: image_fn(data.index[i], palette=pone),
                          GridChartLabelPosition.RIGHT: lambda i: topword_fn(data.index[i], palette=pthree)
                      })

    # legend
    BIG_KEY = round(BOX_SIZE*1.5)
    SMALL_KEY = round(BIG_KEY/2)
    FONT_SIZE = round(18 * SCALE)
    MAX_WIDTH = round(200 * SCALE)
    MAX_WIDTH2 = round(250 * SCALE)

    type_boxes = Image.from_array([
        [image_fn(('a', 0.01), pone, size=BIG_KEY),
         Image.from_text("Letters and spaces sorted by overall frequency. Ignores case.", FONT(FONT_SIZE), padding=(BOX_SIZE//4,0), max_width=MAX_WIDTH)],
        [image_fn(('n', 0.01), ptwo, row='d', size=BIG_KEY),
         Image.from_text("Next letter sorted by frequency. Small letter is the most common third letter following the pair.", FONT(FONT_SIZE), padding=(BOX_SIZE//4,0), max_width=MAX_WIDTH)],
        [image_fn(('of', 0.01), pthree, size=BIG_KEY),
         Image.from_text("Most common word starting with the row's letter in this corpus.", FONT(FONT_SIZE), padding=(BOX_SIZE // 4, 0), max_width=MAX_WIDTH)],
    ], bg="white", xalign=0, padding=(0,BOX_SIZE//20))
    type_leg = Image.from_column([
        Image.from_text("Colour key", FONT(FONT_SIZE, bold=True), max_width=type_boxes.width),
        type_boxes,
        Image.from_text(f"Blank squares indicate spaces.{NOTE}", FONT(FONT_SIZE), max_width=type_boxes.width)],
        bg="white", xalign=0, padding=(0,BOX_SIZE//20))

    color_from_index = lambda i: 10 ** ((i - 6) / 2)
    color_label = lambda i: "{:.1%} to {:.1%}".format(color_from_index(i-1), color_from_index(i))
    freq_boxes = Image.from_array([
        [Image.new("RGBA", (SMALL_KEY,SMALL_KEY), pone[i]),
         Image.new("RGBA", (SMALL_KEY,SMALL_KEY), ptwo[i]),
         Image.new("RGBA", (SMALL_KEY, SMALL_KEY), pthree[i]),
         Image.from_text(color_label(i), FONT(FONT_SIZE), padding=(BOX_SIZE//4,0))]
         for i in reversed(range(0, 7))], bg="white", xalign=0)
    freq_leg = Image.from_column([Image.from_text("Letter/word frequencies", FONT(FONT_SIZE, bold=True)), freq_boxes], bg="white", xalign=0, padding=(0,BOX_SIZE//8))

    legend_inner = Image.from_column([type_leg, freq_leg], bg="white", xalign=0, padding=BOX_SIZE//8)
    legend = legend_inner.pad(SCALE, "black").pad((BOX_SIZE//2,0,BOX_SIZE//4,0), "white")

    num_words = {"cy": 18, "it": 20, "ga": 8}.get(lang, 24)
    words = sorted(render_words(lang, letters, num_words))
    word_array = Image.from_array([
        [Image.from_text(words[i], UFONT(FONT_SIZE, italics=True), fg="black", bg="white"),
         Image.from_text(words[num_words//2 + i ], UFONT(FONT_SIZE, italics=True), fg="black", bg="white")] for i in
        range(len(words) // 2)], bg="white", padding=(15, 2)).pad(BOX_SIZE // 8, "white")
    word_title = Image.from_column([Image.from_text("Markov generators".upper(), FONT(FONT_SIZE, bold=True)),
                                    Image.from_text(
                                        "The letters distributions in the chart can be used to generate pseudowords such as the ones below. A similar approach, at the word level, is used for online parody generators.",
                                        FONT(FONT_SIZE), max_width=MAX_WIDTH2)], bg="white", xalign=0,
                                   padding=(0, BOX_SIZE // 8))
    word_box = Image.from_column([word_title, word_array], bg="white", padding=BOX_SIZE // 8)
    word_box = word_box.pad_to_aspect(legend_inner.width, word_box.height, align=0, bg="white").pad(SCALE, "white").pad(
        (BOX_SIZE // 2, 0, BOX_SIZE // 4, 0), "white")

    chart = Image.from_row([grid, legend], bg="white", yalign=0)
    chart = chart.place(word_box, align=1, padding=(0, BOX_SIZE // 2))
    title = Image.from_column([Image.from_text(TITLE, FONT(BOX_SIZE, bold=True), padding=(10*SCALE, 0), bg="white"),
    Image.from_text(SUBTITLE, FONT(round(24 * SCALE), bold=True), padding=(0,BOX_SIZE//4    ,0,0), bg="white")])
    full = Image.from_column([title, chart], bg="white", padding=(0,BOX_SIZE//4))
    full.place(Image.from_text("/u/Udzu", FONT(16 * SCALE), fg="black", bg="white", padding=5*SCALE).pad((SCALE,SCALE,0,0), "black"), align=1, padding=10*SCALE, copy=False)
    full.save("output/ngrams_grid_{}{}.png".format(lang, suffix))


LETTERS = {
    "cs": ascii + "áčďéěíňóřšťúůýž",
    "cy": strip_any(ascii, "kqvxz"),
    "de": ascii + "äöüß",
    "el": "αβγδεζηθικλμνξοπρσςτυφχψω",
    "en": ascii,
    "es": ascii + "ñ",
    "fi": ascii + "åäöšž",
    "fr": ascii,
    "he": "אבגדהוזחטיכךלמםנןסעפףצץקרשת",
    "hu": ascii + "áéíóöőúüű",
    "id": ascii,
    "it": strip_any(ascii, "jkwxy"),
    "nl": ascii,
    "pl": ascii + "ąćęłńóśźż",
    "pt": ascii,
    "ro": ascii + "ăâîșț",
    "ru": "абвгдеёжзийклмнопрстуфхцчшщъыьэюя",
    "sv": ascii + "åäö",
    "tr": strip_any(ascii, "qwx") + "çğıöşü",
    "uk": "абвгґдеєжзиіїйклмнопрстуфхцчшщьюя",
    "vi": strip_any(ascii, "fjwz") + "ăâêôơưđ",

    "haw": "aeiouhklmnpwʻ",
    "ko": "ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ",
    "sw": strip_any(ascii, "qx"),
    "ga": strip_any(ascii, "jkqvwxyz"),
    "sco": ascii,
}

# TODO: vietnamese, ukrainian, indonesian

NOTES = {
    "cs": "CH is counted as two letters.",
    "cy": "Digraphs are counted as separate letters.",
    "nl": "IJ is counted as two letters.",
    "hu": "Digraphs and trigraphs are counted as separate letters.",
    "vi": "Polysyllabic words are counted as separate words.",
}

def mainly(lang):
    main(lang, LETTERS[lang] + " ", NOTES.get(lang))

def renderly(lang, n=40, min=3, max=10):
    return render_words(lang, LETTERS[lang] + " ", n, min, max, save = False, overwrite= True)

def toply(lang):
    return make_topwords(lang, LETTERS[lang] + " ")

# LANGS = LETTERS
# for lang in tqdm(LANGS):
# #    xextract_wikidump(lang)
#     mainly(lang)
