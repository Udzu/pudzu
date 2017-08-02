import pickle
import seaborn as sns
import string
import sys
sys.path.append('..')

from markov import *
from records import *
from charts import *
from math import log

def train_gutenberg(n):
    logger.info("Training gutenberg {}-grams".format(n))
    try:
        with open("markovtext{}.p".format(n), "rb") as f:
            return pickle.load(f)
    except:
        import nltk.corpus as corpus
        alphaspace = string.ascii_letters + ' '
        markov = MarkovGenerator(n)
        for f in tqdm.tqdm(corpus.gutenberg.fileids()):
            file = str(corpus.gutenberg.abspath(f))
            encoding = corpus.gutenberg.encoding(f)
            markov.train_file(file, encoding=encoding, normalise=lambda i: (c.lower() for c in i if c in alphaspace))
        with open("markovtext{}.p".format(n), "wb") as f:
            pickle.dump(markov, f, pickle.HIGHEST_PROTOCOL)
        return markov

# 1-gram grid
gen = train_gutenberg(1)
alphaspace = string.ascii_lowercase + ' '
index = sorted([(x, gen.prob_dict[(x,)] / sum(gen.prob_dict.values())) for x in alphaspace], key=lambda p: p[1], reverse=True)
array = [[(y,n / sum(gen.markov_dict[(x,)].values())) for y,n in gen.markov_dict[(x,)].most_common()] for x,_ in index]
data = pd.DataFrame(array, index=index)

blues = ImageColor.from_floats(sns.color_palette("Blues", 8))
reds = ImageColor.from_floats(sns.color_palette("Reds", 8))
color_index = lambda p: 0 if p == 0 else delimit(6 + int(log(p, 10) * 2), 0, 6)

def image_fn(pair, palette=blues):
    if pair is None: return None
    img = Image.new("RGBA", (20,20), palette[color_index(pair[1])])
    img.place(Image.from_text(pair[0], arial(10), "black", bg=palette[color_index(pair[1])]), copy=False)
    return img
 
logger.info("Generating grid chart") 
grid = grid_chart(data, image_fn, fg="black", bg="white", padding=1, row_label=lambda i: image_fn(data.index[i], reds))
grid.show()
