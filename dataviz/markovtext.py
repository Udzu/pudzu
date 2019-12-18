import pickle
import seaborn as sns
import string

from pudzu.sandbox.markov import *
from pudzu.sandbox.bamboo import *
from pudzu.charts import *
from math import log

CORPUS = "wikienglish"
TITLE = "Letter and next-letter frequencies in English"
SUBTITLE = "measured across 1 million sentences from Wikipedia"
ENCODING = "utf-8"
LETTERS = string.ascii_lowercase + ' '

# Markov generators

def load_generator(n):
    try:
        logger.info("Loading ../corpora/{}_{}.p".format(CORPUS, n))
        with open("../corpora/{}_{}.p".format(CORPUS, n), "rb") as f:
            return pickle.load(f)
    except:
        logger.info("Training {} {}-grams".format(CORPUS, n))
        markov = MarkovGenerator(n)
        for f in tqdm.tqdm(CORPUS.split("-")):
            markov.train_file("../corpora/"+f, encoding=ENCODING, normalise=partial(latin_normalise, letters=LETTERS))
        logger.info("Saving to ../corpora/{}_{}.p".format(CORPUS, n))
        with open("../corpora/{}_{}.p".format(CORPUS, n), "wb") as f:
            pickle.dump(markov, f, pickle.HIGHEST_PROTOCOL)
        return markov

g1 = load_generator(1)
g2 = load_generator(2)

# Grid chart

SCALE = 2
BOX_SIZE = 40 * SCALE
BIG_KEY = round(BOX_SIZE*1.5)
SMALL_KEY = round(BIG_KEY/2)
FONT_SIZE = round(18 * SCALE)
MAX_WIDTH = round(200 * SCALE)
MAX_WIDTH2 = round(280 * SCALE)

logger.info("Generating grid chart") 
index = sorted([(x, g1.prob_dict[(x,)] / sum(g1.prob_dict.values())) for x in LETTERS if (x,) in g1.prob_dict], key=lambda p: p[1], reverse=True)
array = [[(y,n / sum(g1.markov_dict[(x,)].values())) for y,n in g1.markov_dict[(x,)].most_common()] for x,_ in index]
data = pd.DataFrame(array, index=index)

pone = tmap(RGBA, sns.color_palette("Reds", 8))
ptwo = tmap(RGBA, sns.color_palette("Blues", 8))
color_index = lambda p: 0 if p == 0 else clip(6 + int(log(p, 10) * 2), 0, 6)

def image_fn(pair, palette, row=None, size=BOX_SIZE):
    if pair is None: return None
    bg = palette[color_index(pair[1])]
    img = Image.new("RGBA", (size,size), bg)
    img.place(Image.from_text(pair[0], arial(size//2), "black", bg=bg), copy=False)
    if row is not None and pair[0] != " ":
        if not isinstance(row, str):
            twogram = g2.markov_dict[(index[row][0], pair[0])].most_common()
            row, _ = twogram[0][0], twogram[0][1] / sum(n for _,n in twogram)
        img.place(Image.from_text(row, arial(round(size/3.5)), "black", bg=bg), align=(1,0), padding=(size//8,size//5), copy=False)
    return img
 
grid = grid_chart(data, lambda p, r: image_fn(p, row=r, palette=ptwo), fg="black", bg="white", padding=round(SCALE), row_label=lambda i: image_fn(data.index[i], palette=pone))

# Main legend

type_boxes = Image.from_array([
    [image_fn(('a', 0.01), pone, size=BIG_KEY),
     Image.from_text("Letters and spaces sorted by overall frequency. Ignores case and accents.", arial(FONT_SIZE), padding=(BOX_SIZE//4,0), max_width=MAX_WIDTH)],
    [image_fn(('n', 0.01), ptwo, row='d', size=BIG_KEY),
     Image.from_text("Next letter sorted by frequency. Small letter is the most common third letter following the pair.", arial(FONT_SIZE), padding=(BOX_SIZE//4,0), max_width=MAX_WIDTH)]
], bg="white", xalign=0, padding=(0,BOX_SIZE//20))
type_leg = Image.from_column([Image.from_text("Colour key", arial(FONT_SIZE, bold=True)), type_boxes, Image.from_text("Blank letters indicate spaces.", arial(FONT_SIZE))], bg="white", xalign=0, padding=(0,BOX_SIZE//20))

color_from_index = lambda i: 10 ** ((i - 6) / 2)
color_label = lambda i: "{:.1%} to {:.1%}".format(color_from_index(i-1), color_from_index(i))
freq_boxes = Image.from_array([
    [Image.new("RGBA", (SMALL_KEY,SMALL_KEY), "white" if i == 6 else pone[i]),
     Image.new("RGBA", (SMALL_KEY,SMALL_KEY), ptwo[i]),
     Image.from_text(color_label(i), arial(FONT_SIZE), padding=(BOX_SIZE//4,0))]
     for i in reversed(range(0, 7))], bg="white", xalign=0)
freq_leg = Image.from_column([Image.from_text("Letter frequencies", arial(FONT_SIZE, bold=True)), freq_boxes], bg="white", xalign=0, padding=(0,BOX_SIZE//8))

legend_inner = Image.from_column([type_leg, freq_leg], bg="white", xalign=0, padding=BOX_SIZE//8)
legend = legend_inner.pad(SCALE, "black").pad((BOX_SIZE//2,0,BOX_SIZE//4,0), "white")

# Generated words

if CORPUS == "wikienglish":
    words = ["bastrabot", "dithely", "foriticent", "gamplato", "calpereek", "amorth", "forliatitive", "asocult", "wasions", "quarm", "felogy", "winferlifterand", "loubing", "uniso", "fourn", "hise", "meembege", "whigand", "prouning", "guncelawits", "nown", "rectere", "abrip", "doesium"]
elif CORPUS == "wikifrench":
    words = ["cillesil", "sulskini", "lidhemin", "plumeme", "bachogine", "crout", "taphie", "provicas", "copit", "odzzaccet", "extreiles", "pipiphien", "chetratagne", "outif", "suro", "extellages", "nans", "nutopune", "entote", "sporese", "zhiquis", "edes", "aliet", "randamelle"]
else:
    words = [g2.render_word() for i in range(24)]
    
word_array = Image.from_array([
    [Image.from_text(words[2*i], arial(FONT_SIZE, italics=True), fg="black", bg="white"),
     Image.from_text(words[2*i+1], arial(FONT_SIZE, italics=True), fg="black", bg="white")] for i in range(len(words)//2)], bg="white", padding=(15,2)).pad(BOX_SIZE//8,"white")
word_title = Image.from_column([Image.from_text("Markov generators", arial(FONT_SIZE, bold=True)), 
Image.from_text("The letters distributions in the chart can be used to generate pseudowords such as the ones below. A similar approach, at the word level, is used for online parody generators.", arial(FONT_SIZE),max_width=MAX_WIDTH2)], bg="white", xalign=0, padding=(0,BOX_SIZE//8))
word_box = Image.from_column([word_title, word_array], bg="white", padding=BOX_SIZE//8)
word_box = word_box.pad_to_aspect(legend_inner.width, word_box.height, align=0, bg="white").pad(SCALE, "white").pad((BOX_SIZE//2,0,BOX_SIZE//4,0), "white")

# Chart

chart = Image.from_row([grid, legend], bg="white", yalign=0)
chart = chart.place(word_box, align=1, padding=(0,BOX_SIZE))
title = Image.from_column([Image.from_text(TITLE, arial(BOX_SIZE, bold=True), bg="white"),
Image.from_text(SUBTITLE, arial(round(24 * SCALE), bold=True), bg="white")])
full = Image.from_column([title, chart], bg="white", padding=(0,BOX_SIZE//4))
full.save("output/markovtext_{}.png".format(CORPUS))

