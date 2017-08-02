import nltk.corpus as corpus
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
    try:
        with open("markovtext{}.p".format(n), "rb") as f:
            return pickle.load(f)
    except:
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
array = [[(y,n / sum(gen.markov_dict[(x,)].values())) for y,n in gen.markov_dict[(x,)].most_common()] for x in alphaspace]
data = pd.DataFrame(array, index=[(x, gen.prob_dict[(x,)] / sum(gen.prob_dict.values())) for x in alphaspace])

blues = ImageColor.from_floats(sns.color_palette("Blues", 8))
reds = ImageColor.from_floats(sns.color_palette("Reds", 8))
color_index = lambda p: 0 if p == 0 else delimit(6 + int(log(p, 10) * 2), 0, 6)

def image_fn(pair, palette=blues):
    if pair is None: return None
    img = Image.new("RGBA", (20,20), palette[color_index(pair[1])])
    img.place(Image.from_text(pair[0], arial(10), "black", bg=palette[color_index(pair[1])]), copy=False)
    return img
    
grid = grid_chart(data, image_fn, fg="black", bg="white", padding=1, row_label=lambda i: image_fn(data.index[i], reds))

# n-gram examples
gens = [train_gutenberg(i+1) for i in tqdm.tqdm(range(5))]
def gen_words(gen):
    while True:
        word = "".join(gen.render(" ", start_if=lambda t: (t[0] == " ") and (" " not in t[1:])))[:-1]
        if len(word) >= 3:
            yield word
words = [list(itertools.islice(gen_words(gens[i]), 20)) for i in tqdm.tqdm(range(5))]
rs = [make_mapping(c, lambda i: str(i+1)) for c in zip(*words)]
RecordCSV.save_file("markovtext.csv", rs, delimiter="\t")

rs = RecordCSV.load_file("markovtext.csv", delimiter="\t")
entries = [[Image.from_text(r[str(i)], arial(12), fg="black", bg="white") for i in range(1,6)] for r in rs]
headings = [Image.from_text(str(i), arial(12, bold=True), fg="black", bg="white")  for i in range(1,6)]
entries.insert(0, headings)
table = Image.from_array(entries, bg="white", padding=(4,2))

# explanation
