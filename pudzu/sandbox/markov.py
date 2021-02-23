import argparse
import bisect
import functools
import itertools
import operator as op
import pickle
import random
import string
import sys
import unicodedata
from collections import Counter

# Simple Markov n-gram based generator.


def generate_ngrams(iterable, n):
    """Generator that yields n-grams from a sequence."""
    return zip(*[itertools.islice(it, i, None) for i, it in enumerate(itertools.tee(iterable, n))])


def counter_random(counter, filter=None):
    """Return a single random elements from the Counter collection, weighted by count."""
    if filter is not None:
        counter = {k: v for k, v in counter.items() if filter(k)}
    if len(counter) == 0:
        raise Exception("No matching elements in Counter collection")
    seq = list(counter.keys())
    cum = list(itertools.accumulate(list(counter.values()), op.add))
    return seq[bisect.bisect_left(cum, random.uniform(0, cum[-1]))]


def latin_normalise(i, letters=string.ascii_letters + " ", lowercase=True):
    """Example normalisation function that strips everything apart from letters and spaces (even accents)."""
    return (nc for c in i for cc in (c.lower() if lowercase else c) for nc in (cc if cc in letters else unicodedata.normalize("NFKD", cc)) if nc in letters)


class MarkovGenerator(object):
    """Markov Chain n-gram-based generator for arbitrary iterables."""

    def __init__(self, order):
        """Initialise generator for a given n-gram order."""
        self.n = order
        self.markov_dict = {}
        self.prob_dict = Counter()

    def reset(self):
        """Reset generator."""
        self.__init__(self.n)

    def train(self, iterable):
        """Train generator on an iterable."""
        for ngram in generate_ngrams(iterable, self.n + 1):
            self.markov_dict.setdefault(ngram[: self.n], Counter()).update([ngram[self.n]])
            self.prob_dict.update([ngram[: self.n]])

    def train_file(self, filename, encoding="utf-8", convert=itertools.chain.from_iterable, normalise=lambda i: i):
        """Train generator on a file. Accepts optional convert function (defaults to reading characters) and
        normalise function (defaults to the identity)."""
        with open(filename, "r", encoding=encoding) as f:
            self.train(normalise(convert(f)))

    def render(self, stop_when, start_ngram=None):
        """Return a tuple using the trained probabilities. Stop condition can be a maximum length or function."""
        stop_fn = stop_when if callable(stop_when) else lambda o: len(o) >= stop_when
        start_fn = start_ngram if (callable(start_ngram) or start_ngram is None) else lambda n: n == tuple(start_ngram)
        ngram = counter_random(self.prob_dict, filter=start_fn)
        output = ngram
        while True:
            if stop_fn(output):
                break
            elif ngram in self.markov_dict:
                v = counter_random(self.markov_dict[ngram])
                output += (v,)
                ngram = ngram[1:] + (v,)
            else:
                ngram = counter_random(self.prob_dict)
        return output

    def render_word(self, min_length=3, max_length=12):
        """Generates a word. Assumes training on characters including spaces.
        Doesn't filter out real words."""
        while True:
            word = "".join(self.render(lambda o: len(o) > 1 and o[-1] == " ", lambda n: n[0] == " "))
            if min_length <= len(word.strip()) <= max_length:
                return word.strip()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate pseudowords using Markov chains")
    parser.add_argument("corpus", type=str, help="text corpus name")
    parser.add_argument("number", type=int, help="number of words to generate")
    parser.add_argument("-n", "--order", type=int, help="n-gram order [2]", default=2)
    parser.add_argument("-l", "--letters", type=str, help="letters to keep [a-z/A-Z]", default=string.ascii_letters)
    parser.add_argument("-c", "--casesensitive", action="store_true", help="case sensitive generator [False]")
    parser.add_argument("-r", "--regenerate", action="store_true", help="always regenerate generator [False]")
    args = parser.parse_args()

    pickled_dict = "{}_{}.p".format(args.corpus, args.order)
    try:
        if args.regenerate:
            raise FileNotFoundError
        print("Checking for cached generator at {}".format(pickled_dict), file=sys.stderr)
        with open(pickled_dict, "rb") as f:
            mk = pickle.load(f)
    except FileNotFoundError:
        print("Training from corpus (may take a while).", file=sys.stderr)
        mk = MarkovGenerator(order=args.order)
        mk.train_file(args.corpus, normalise=functools.partial(latin_normalise, letters=args.letters + " ", lowercase=not args.casesensitive))
        print("Saving generated generator to {}".format(pickled_dict), file=sys.stderr)
        with open(pickled_dict, "wb") as f:
            pickle.dump(mk, f, pickle.HIGHEST_PROTOCOL)
    for i in range(args.number):
        print(mk.render_word())
