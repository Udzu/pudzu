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

CORPUS = "-wikifrench"
TITLE = "Letter and next-letter frequencies in French"
SUBTITLE = "measured across a selection of text from Wikipedia"
LETTERS = string.ascii_lowercase + ' '

def normalise(i):
    return (nc for c in i for nc in unicodedata.normalize('NFKD', c).lower() if nc in LETTERS)
    
def train_nltk_corpus(corpus, n):
    try:
        logger.info("Loading markovtext_{}_{}.p".format(corpus, n))
        with open("markovtext_{}_{}.p".format(corpus, n), "rb") as f:
            return pickle.load(f)
    except:
        logger.info("Training {} {}-grams".format(corpus, n))
        markov = MarkovGenerator(n)
        corpusname, *files = corpus.split("-")
        if corpusname:
            nltk_corpus = optional_import_from("nltk.corpus", corpusname)
            for f in tqdm.tqdm(files if len(files) > 0 else nltk_corpus.fileids()):
                file = str(nltk_corpus.abspath(f))
                encoding = nltk_corpus.encoding(f)
                markov.train_file(file, encoding=encoding, normalise=normalise)
        else:
            for f in tqdm.tqdm(files):
                markov.train_file(f, encoding="utf-8", normalise=normalise)
        logger.info("Saving markovtext_{}_{}.p".format(corpus, n))
        with open("markovtext_{}_{}.p".format(corpus, n), "wb") as f:
            pickle.dump(markov, f, pickle.HIGHEST_PROTOCOL)
        return markov

# 1-gram grid
g1 = train_nltk_corpus(CORPUS, 1)
g2 = train_nltk_corpus(CORPUS, 2)
index = sorted([(x, g1.prob_dict[(x,)] / sum(g1.prob_dict.values())) for x in LETTERS if (x,) in g1.prob_dict], key=lambda p: p[1], reverse=True)
array = [[(y,n / sum(g1.markov_dict[(x,)].values())) for y,n in g1.markov_dict[(x,)].most_common()] for x,_ in index]
data = pd.DataFrame(array, index=index)

pone = ImageColor.from_floats(sns.color_palette("Reds", 8))
ptwo = ImageColor.from_floats(sns.color_palette("Blues", 8))
pthree = ImageColor.from_floats(sns.color_palette("Purples", 8))
color_index = lambda p: 0 if p == 0 else delimit(6 + int(log(p, 10) * 2), 0, 6)

def image_fn(pair, palette, row=None):
    if pair is None: return None
    bg = palette[color_index(pair[1])]
    img = Image.new("RGBA", (40,40), bg)
    img.place(Image.from_text(pair[0], arial(20), "black", bg=bg), copy=False)
    if row is not None and pair[0] != " ":
        if not isinstance(row, str):
            twogram = g2.markov_dict[(index[row][0], pair[0])].most_common()
            row, _ = twogram[0][0], twogram[0][1] / sum(n for _,n in twogram)
        img.place(Image.from_text(row, arial(10), "black", bg=bg), align=(1,0), padding=(4,2), copy=False)
    return img
 
logger.info("Generating grid chart") 
grid = grid_chart(data, lambda p, r: image_fn(p, row=r, palette=ptwo), fg="black", bg="white", padding=1, row_label=lambda i: image_fn(data.index[i], palette=pone))

# legend
font_size = 12

type_boxes = Image.from_array([
[image_fn(('a', 0.01), pone), Image.from_text("Letters and spaces sorted by frequency. Ignores case and accents.", arial(font_size), padding=(10,0), max_width=150)],
[image_fn(('n', 0.01), ptwo, row='d'), Image.from_text("Subsequent letter sorted by frequency. Small letter is the most common third letter following the pair.", arial(font_size), padding=(10,0), max_width=150)]
], bg="white", xalign=0, padding=(0,2))
type_leg = Image.from_column([Image.from_text("Letter type", arial(font_size, bold=True)), type_boxes, Image.from_text("Blank letters indicate spaces", arial(font_size))], bg="white", xalign=0, padding=(0,2))

color_from_index = lambda i: 10 ** ((i - 6) / 2)
color_label = lambda i: "{:.1%} to {:.1%}".format(color_from_index(i-1), color_from_index(i))
freq_boxes = Image.from_array([[Image.new("RGBA", (20,20), "white" if i == 6 else pone[i]), Image.new("RGBA", (20,20), ptwo[i]), Image.from_text(color_label(i), arial(font_size), padding=(10,0))] for i in reversed(range(0, 7))], bg="white", xalign=0)
freq_leg = Image.from_column([Image.from_text("Letter frequencies", arial(font_size, bold=True)), freq_boxes], bg="white", xalign=0, padding=(0,5))

legend = Image.from_column([type_leg, freq_leg], bg="white", xalign=0, padding=5).pad(1, "black").pad((20,0,10,0), "white")

# chart
chart = Image.from_row([grid, legend], bg="white", yalign=0)
title = Image.from_column([Image.from_text(TITLE, arial(40, bold=True), bg="white"),
Image.from_text(SUBTITLE, arial(24, bold=True), bg="white")])
full = Image.from_column([title, chart], bg="white", padding=(0,10))
full.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
full.save("markovtext_{}.png".format(CORPUS))


