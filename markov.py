import random
import itertools

from utils import *
from collections import Counter
from numbers import Integral

class MarkovGenerator(object):
    """Markov Chain n-gram-based generator for aribtrary iterables."""
    
    def __init__(self, order):
        self.n = order
        self.markov_dict = {}
        self.prob_dict = Counter()
        
    def reset(self):
        self.__init__(self.n)
        
    def train(self, iterable):
        for ngram in generate_ngrams(iterable, self.n+1):
            self.markov_dict.setdefault(ngram[:self.n], Counter()).update([ngram[self.n]])
            self.prob_dict.update([ngram[:self.n]])
            
    def train_file(self, filename, encoding="utf-8", convert=itertools.chain.from_iterable, normalise=identity):
        with open(filename, "r", encoding=encoding) as f:
            self.train(normalise(convert(f)))
            
    def render(self, stop_if, start_if=None):
        stop_fn = (stop_if if callable(stop_if) else
                   (lambda o: len(o) >= stop_if) if isinstance(stop_if, Integral) else
                   (lambda o: o and o[-1] == stop_if))
        output = ()
        while True:
            ngram = self.prob_dict.random()
            if start_if is None or start_if(ngram):
                break # might take ages if you're not careful
        while True:
            if stop_fn(output):
                break
            elif ngram in self.markov_dict:
                v = self.markov_dict[ngram].random()
                output += (v,)
                ngram = ngram[1:] + (v,)
            else:
                ngram = self.prob_dict.random()
        return output
