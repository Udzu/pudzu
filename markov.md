# [markov.py](markov.py)

## Summary 
Simple Markov Chain n-gram based generator, supporting arbitrary iterables. 

## Dependencies
None. 

## Documentation

**MarkovGenerator**: a simple Markov Chain n-gram based generator. 

```python
>> mk = MarkovGenerator(order=1) # use 1-grams (i.e. single elements)
>> mk.train("The rain in Spain")
>> mk.train("The food in Mexico")
>> mk.render(10)

>> mk.reset()
>> mk.train((1,2,3,2,3,1))
>> mk.render(10)

```

N-grams can be trained directly from files, with an optional method to convert the file iterable (which defaults to extracting characters) and another to normalise it (which defaults to doing nothing). A sample normalising function, latin_normalise, is provided, which strips accents and all non-Latin characters, and lower cases the input. To avoid high memory footprints, normalisers should be written as generators. 

```python
>> mk = MarkovGenerator(order=2) # use 2-grams (i.e. pairs of elements)
>> mk.train_file("warandpeace.txt", normalise=latin_normalise)
# [...takes a while...]
>> for i in range(3): print(mk.render_word())
pring
hetedly
nued
```

To avoid having to regenerate the probability dictionary each time, you can pickle the MarkovGenerator object:

```python
>> import pickle
>> with open("warandpeace_2grams.p", "wb") as f:
       pickle.dump(mk, f, pickle.HIGHEST_PROTOCOL)
```

And then unpickle it later:

```python
>> with open("warandpeace_2grams.p", "rb") as f:
       mk = pickle.load(f)
```

### Word generation

Note that *render_word* assumes that the generator was trained on character data including spaces (which are used to detect pseudoword boundaries). It doesn't filter out real words. 