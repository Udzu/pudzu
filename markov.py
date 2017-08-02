import random

from utils import *
from collections import Counter

class MarkovGenerator(object):
    """Markov Chain n-gram-based generator for aribtrary iterable types."""
    
    def __init__(self, order):
        self.n = order
        self.markov_dict = {}
        self.prob_dict = Counter()
        
    def train(self, iterable):
        for ngram in generate_ngrams(iterable, self.n+1):
            self.markov_dict.setdefault(ngram[:self.n], Counter()).update([ngram[self.n]])
            self.prob_dict.update([ngram[:self.n]])
            
    def render(self, length):
        output = ()
        ngram = self.prob_dict.random()
        for i in range(length):
            if ngram in self.markov_dict:
                v = self.markov_dict[ngram].random()
                output += (v,)
                ngram = ngram[1:] + (v,)
            else:
                ngram = self.prob_dict.random()
        return output
