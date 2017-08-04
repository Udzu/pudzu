import pickle
import seaborn as sns
import string
import sys
import unicodedata
sys.path.append('..')

from markov import *
from records import *
from charts import *
from math import log

CORPUS = "-wikienglish"
TITLE = "Letter and next-letter frequencies in English"
SUBTITLE = "measured across 1 million articles from Wikipedia"

# CORPUS = "-wikifrench"
# TITLE = "Letter and next-letter frequencies in French"
# SUBTITLE = "measured across a selection of articles from Wikipedia"

# CORPUS = "gutenberg"
# TITLE = "Letter and next-letter frequencies in English"
# SUBTITLE = "measured using the NLTK Gutenberg corpus"

letters = string.ascii_lowercase + ' '
corpusname, *corpusfiles = CORPUS.split("-")
filebase = "markovtext_{}".format(CORPUS.lstrip("-"))

def normalise(i):
    return (nc for c in i for nc in unicodedata.normalize('NFKD', c).lower() if nc in letters)
    
def train_corpus(corpus, n):
    try:
        logger.info("Load {}_{}.p".format(filebase, n))
        with open("{}_{}.p".format(filebase, n), "rb") as f:
            return pickle.load(f)
    except:
        logger.info("Training {} {}-grams".format(corpus, n))
        markov = MarkovGenerator(n)
        if corpusname:
            nltk_corpus = optional_import_from("nltk.corpus", corpusname)
            for f in tqdm.tqdm(files if len(corpusfiles) > 0 else nltk_corpus.fileids()):
                file = str(nltk_corpus.abspath(f))
                encoding = nltk_corpus.encoding(f)
                markov.train_file(file, encoding=encoding, normalise=normalise)
        else:
            for f in tqdm.tqdm(corpusfiles):
                markov.train_file(f, encoding="utf-8", normalise=normalise)
        logger.info("Save to {}_{}.p".format(filebase, n))
        with open("{}_{}.p".format(filebase, n), "wb") as f:
            pickle.dump(markov, f, pickle.HIGHEST_PROTOCOL)
        return markov

g1 = train_corpus(CORPUS, 1)
g2 = train_corpus(CORPUS, 2)

# grid chart
logger.info("Generating grid chart") 
index = sorted([(x, g1.prob_dict[(x,)] / sum(g1.prob_dict.values())) for x in letters if (x,) in g1.prob_dict], key=lambda p: p[1], reverse=True)
array = [[(y,n / sum(g1.markov_dict[(x,)].values())) for y,n in g1.markov_dict[(x,)].most_common()] for x,_ in index]
data = pd.DataFrame(array, index=index)

csvarray = [["{} [{:.1%}]".format(*p) for p in r] for r in array]
csvindex = ["{} [{:.1%}]".format(*p) for p in index]
csvdata = pd.DataFrame(csvarray, index=csvindex)
csvdata.to_csv("{}.csv".format(filebase))

pone = ImageColor.from_floats(sns.color_palette("Reds", 8))
ptwo = ImageColor.from_floats(sns.color_palette("Blues", 8))
color_index = lambda p: 0 if p == 0 else delimit(6 + int(log(p, 10) * 2), 0, 6)

def image_fn(pair, palette, row=None, size=40):
    if pair is None: return None
    bg = palette[color_index(pair[1])]
    img = Image.new("RGBA", (size,size), bg)
    img.place(Image.from_text(pair[0], arial(size//2), "black", bg=bg), copy=False)
    if row is not None and pair[0] != " ":
        if not isinstance(row, str):
            twogram = g2.markov_dict[(index[row][0], pair[0])].most_common()
            row, _ = twogram[0][0], twogram[0][1] / sum(n for _,n in twogram)
        img.place(Image.from_text(row, arial(size//4), "black", bg=bg), align=(1,0), padding=(size//10,size//5), copy=False)
    return img
 
grid = grid_chart(data, lambda p, r: image_fn(p, row=r, palette=ptwo), fg="black", bg="white", padding=1, row_label=lambda i: image_fn(data.index[i], palette=pone))

# main legend
font_size = 18

type_boxes = Image.from_array([
    [image_fn(('a', 0.01), pone, size=60),
     Image.from_text("Letters and spaces sorted by overall frequency. Ignores case and accents.", arial(font_size), padding=(10,0), max_width=200)],
    [image_fn(('n', 0.01), ptwo, row='d', size=60),
     Image.from_text("Next letter sorted by frequency. Small letter is the most common third letter following the pair.", arial(font_size), padding=(10,0), max_width=200)]
], bg="white", xalign=0, padding=(0,2))
type_leg = Image.from_column([Image.from_text("Colour key", arial(font_size, bold=True)), type_boxes, Image.from_text("Blank letters indicate spaces", arial(font_size))], bg="white", xalign=0, padding=(0,2))

color_from_index = lambda i: 10 ** ((i - 6) / 2)
color_label = lambda i: "{:.1%} to {:.1%}".format(color_from_index(i-1), color_from_index(i))
freq_boxes = Image.from_array([
    [Image.new("RGBA", (30,30), "white" if i == 6 else pone[i]),
     Image.new("RGBA", (30,30), ptwo[i]),
     Image.from_text(color_label(i), arial(font_size), padding=(10,0))]
     for i in reversed(range(0, 7))], bg="white", xalign=0)
freq_leg = Image.from_column([Image.from_text("Letter frequencies", arial(font_size, bold=True)), freq_boxes], bg="white", xalign=0, padding=(0,5))

legend_inner = Image.from_column([type_leg, freq_leg], bg="white", xalign=0, padding=5)
legend = legend_inner.pad(1, "black").pad((20,0,10,0), "white")

# markov generated words
def gen_words(gen):
    while True:
        word = "".join(gen.render(lambda o: len(o) > 1 and o[-1] == ' '))
        if 12 >= len(word.strip()) >= 3 and word.startswith(" "):
            yield word.strip()

if CORPUS == "-wikienglish":
    words = ["bastrabot", "dithely", "loctrion", "raliket", "calpereek", "amorth", "forliatitive", "asocult", "wasions", "quarm", "felogy", "winferlifterand", "sonsih", "uniso", "fourn", "hise", "meembege", "nuouish", "prouning", "guncelawits", "nown", "rectere", "abrip", "doesium"]
elif CORPUS == "-wikifrench":
    words = ["cillesil", "sulskini", "lidhemin", "plumeme", "bachogine", "crout", "taphie", "provicas", "copit", "odzzaccet", "extreiles", "pipiphien", "chetratagne", "outif", "suro", "extellages", "nans", "nutopune", "entote", "sporese", "zhiquis", "edes", "aliet", "randamelle"]
else:
    words = [w for w,_ in zip(gen_words(g2), range(24))]
    
word_array = Image.from_array([
    [Image.from_text(words[2*i], arial(font_size, italics=True), fg="black", bg="white"),
     Image.from_text(words[2*i+1], arial(font_size, italics=True), fg="black", bg="white")] for i in range(len(words)//2)], bg="white", padding=(15,2)).pad(5,"white")
word_title = Image.from_column([Image.from_text("Markov generators", arial(font_size, bold=True)), 
Image.from_text("The letters distributions in the chart can be used to generate psuedowords such as the ones below. A similar approach, at the word level, is used for online parody generators.", arial(font_size),max_width=280)], bg="white", xalign=0, padding=(0,5))
word_box = Image.from_column([word_title, word_array], bg="white", padding=5)
word_box = word_box.pad_to_aspect(legend_inner.width, word_box.height, align=0, bg="white").pad(1, "white").pad((20,0,10,0), "white")

# chart
chart = Image.from_row([grid, legend], bg="white", yalign=0)
chart = chart.place(word_box, align=1, padding=(0,75))
title = Image.from_column([Image.from_text(TITLE, arial(40, bold=True), bg="white"),
Image.from_text(SUBTITLE, arial(24, bold=True), bg="white")])
full = Image.from_column([title, chart], bg="white", padding=(0,10))
full.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
full.save("{}.png".format(filebase))

