import pickle
import seaborn as sns
import string
import sys
sys.path.append('..')

from markov import *
from records import *
from charts import *
from math import log

# TODO: normalise accents

CORPUS = "webtext"
LETTERS = string.ascii_lowercase + ' '

def train_nltk_corpus(corpus, n):
    logger.info("Training {} {}-grams".format(corpus, n))
    try:
        with open("markovtext_{}_{}.p".format(corpus, n), "rb") as f:
            return pickle.load(f)
    except:
        nltk_corpus = optional_import_from("nltk.corpus", corpus)
        markov = MarkovGenerator(n)
        for f in tqdm.tqdm(nltk_corpus.fileids()):
            file = str(nltk_corpus.abspath(f))
            encoding = nltk_corpus.encoding(f)
            markov.train_file(file, encoding=encoding, normalise=lambda i: (c.lower() for c in i if c.lower() in LETTERS))
        with open("markovtext_{}_{}.p".format(corpus, n), "wb") as f:
            pickle.dump(markov, f, pickle.HIGHEST_PROTOCOL)
        return markov

# 1-gram grid
g1 = train_nltk_corpus(CORPUS, 1)
g2 = train_nltk_corpus(CORPUS, 2)
index = sorted([(x, g1.prob_dict[(x,)] / sum(g1.prob_dict.values())) for x in LETTERS], key=lambda p: p[1], reverse=True)
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
        twogram = g2.markov_dict[(index[row][0], pair[0])].most_common()
        l, p = twogram[0][0], twogram[0][1] / sum(n for _,n in twogram)
        # bg = pthree[color_index(p)]
        img.place(Image.from_text(l, arial(10), "black", bg=bg), align=(1,0), padding=(4,2), copy=False)
    return img
 
logger.info("Generating grid chart") 
grid = grid_chart(data, lambda p, r: image_fn(p, row=r, palette=ptwo), fg="black", bg="white", padding=1, row_label=lambda i: image_fn(data.index[i], palette=pone))
grid.save("markovtext_{}.png".format(CORPUS))
