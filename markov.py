import mmap
import random

from utils import *
from collections import Counter

# TODO: add filtering, normalisation, improved end condition

class MarkovGenerator(object):
    """Markov Chain n-gram generator. Works on aribtrary sequence types."""
    
    def __init__(self, tuple_length):
        self.tuple_length = tuple_length
        self.markov_dict = {}
        
    def generate_ngrams(self, seq):
        for i in range(0, len(seq) - self.tuple_length):
            yield (seq[i:i+self.tuple_length], seq[i+self.tuple_length:i+self.tuple_length+1])
            
    def train_sequence(self, seq):
        for key, val in self.generate_ngrams(seq):
            self.markov_dict.setdefault(key, Counter()).update([val])
            
    def train_file(self, filename, encoding='utf-8'):
        with open(filename, 'r', encoding=encoding) as file:
            self.train_sequence(file.read())
        
    def train_mmap(self, filename):
        with open(filename, 'r+') as file:
            bytes = mmap.mmap(file.fileno(), 0)
            self.train_sequence(bytes)
        
    def render(self, max_length=100, pre_ngram=None, end_value=None):
        ngram = pre_ngram or random.choice(list(self.markov_dict))
        if len(ngram) != self.tuple_length:
            raise ValueError("Wrong length for start ngram: got {}, expected {}".format(len(ngram), self.tuple_length))
        output = type(ngram)()
        for i in range(len(output), max_length):
            if ngram in self.markov_dict:
                v = random.choice(list(self.markov_dict[ngram].elements()))
                if end_value == v: break
                output += v
                ngram = ngram[1:] + v
            else:
                ngram = random.choice(list(self.markov_dict))
        return output
