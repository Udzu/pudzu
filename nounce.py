from collections import abc
import re

from utils import *

# Pronouncing dictionary class, largely targeted at English

IPA_VOWELS = "ɔɑiuɛɪʊʌəæeaoyʏøɝɚɒɜʁ"
IPA_VOWELENDINGS = IPA_VOWELS + "ː̯̩̃"
IPA_CONSONANTS = "pbtdkɡfvθðszʃʒhmnŋlrɾɹjwʔʍχ"
IPA_STRESS = "ˈˌ"

class Nouncer(abc.MutableMapping):

    PHONEME_PATTERN = ("("
        "[{stress}]|"
        "[{vowel}][ː̃]*[ʊɪə]?[̯]?|"
        "(?:t͡?ʃ|d͡?ʒ|[{consonant}])[̩]?"
    ")[.ˑ ]?".format(stress=IPA_STRESS, vowel=IPA_VOWELS, consonant=IPA_CONSONANTS))

    ARPABET_TO_IPA = {
        'AO': 'ɔ', 'AA': 'ɑ', 'IY': 'i', 'UW': 'u', 'EH': 'ɛ', 'IH': 'ɪ', 'UH': 'ʊ', 'AH': 'ʌ', 'AX': 'ə', 'AE': 'æ',
        'EY': 'eɪ', 'AY': 'aɪ', 'OW': 'oʊ', 'AW': 'aʊ', 'OY': 'ɔɪ', 'ER': 'ɝ', 'AXR': 'ɚ',
        'P': 'p', 'B': 'b', 'T': 't', 'D': 'd', 'K': 'k', 'G': 'ɡ', 'CH': 't͡ʃ', 'JH': 'd͡ʒ', 'F': 'f', 'V': 'v',
        'TH': 'θ', 'DH': 'ð', 'S': 's', 'Z': 'z', 'SH': 'ʃ', 'ZH': 'ʒ', 'HH': 'h', 'M': 'm', 'EM': 'm̩',
        'N': 'n', 'EN': 'n̩', 'NG': 'ŋ', 'ENG': 'ŋ̍', 'L': 'l', 'EL': 'ɫ̩', 'R': 'r', 'DX': 'ɾ', 'NX': 'ɾ̃',
        'Y': 'j', 'W': 'w', 'Q': 'ʔ' }
    
    def __init__(self, filename=None, normalize=str.lower):
        self.pdict = CaseInsensitiveDict(normalize=normalize)
        if filename is not None:
            with open(filename, "r", encoding="utf-8") as f:
                for entry in f:
                    m = re.match("(.*)\t(.*)", entry)
                    if m:
                        self.pdict.setdefault(m.group(1), set()).add(tuple(m.group(2).split(" ")))
        
    def save(self, filename):
        """Save pronuncing dictionary to file."""
        with open(filename, 'w', encoding='utf-8') as f:
            for word in sorted(self.pdict.keys()):
                for pronunciation in self.pdict[word]:
                    print("{}\t{}".format(word, " ".join(pronunciation)), file=f)
     
    def import_cmudict(self, filename):
        """Import pronunciations from CMUDict."""
        with open(filename, "r", encoding="latin-1") as f:
            for entry in f:
                m = re.match("([^(]*)(?:[(][0-9][)])?  (.*)", entry)
                if m:
                    self.pdict.setdefault(m.group(1).lower(), set()).add(self.arpabet_to_phonemes(m.group(2)))
        
    def import_list(self, filename, delimiter="\t", ignore_errors=True):
        """Import pronunciations from a list file."""
        errors = []
        with open(filename, "r", encoding="utf-8") as f:
            for entry in f:
                m = re.match("(.*)[{}](.*)".format(delimiter), entry)
                if m:
                    try:
                        self.pdict.setdefault(m.group(1), set()).update(self.ipa_to_phonemes(m.group(2)))
                    except ValueError as e:
                        if not ignore_errors:
                            raise ValueError("Error reading {}: {}".format(m.group(1), str(e)))
                        errors.append((m.group(1), str(e)))
        return errors
        
    PHONEME_REGEX = re.compile(PHONEME_PATTERN)
    PRONUNCIATION_REGEX = re.compile("(?:{phoneme})*".format(phoneme=PHONEME_PATTERN))
    PARENTHESES_REGEX = re.compile("[(]([^)]+)[)]")
    BRACKETS_REGEX = re.compile("\[([^\]]+)\]")

    def ipa_to_phonemes(self, pronunciation):
        def normalise(string):
            string = re.sub("(?<=.)-(?=.)", "", string)
            return (string.replace('ĭ','i').replace('̈','').replace('ᵻ','[ɪ,ə]')
                          .replace('ɨ','ɪ').replace('ɘ','ə').replace('ɵ','ʊ')
                          .replace('ɱ','m'))
        def expand_parentheses(string):
            m = re.search(self.PARENTHESES_REGEX, string)
            if not m: return expand_brackets(string)
            else: return [x for s in (re.sub(self.PARENTHESES_REGEX, "", string, count=1), re.sub(self.PARENTHESES_REGEX, r"\1", string, count=1)) for x in expand_parentheses(s)]
        def expand_brackets(string):
            m = re.search(self.BRACKETS_REGEX, string)
            if not m: return [string]
            else: return [x for s in (re.sub(self.BRACKETS_REGEX, v, string, count=1) for v in m.group(1).split(",")) for x in expand_brackets(s)]
        pronunciations = expand_parentheses(normalise(pronunciation))
        return [self.ipa_to_phonemes_no_parentheses(p) for p in pronunciations]
        
    def ipa_to_phonemes_no_parentheses(self, pronunciation):
        m = re.match(self.PRONUNCIATION_REGEX, pronunciation)
        if m.end() < len(pronunciation):
            raise ValueError("Invalid pronunciation: /{}**{}/".format(pronunciation[:m.end()], pronunciation[m.end():]))
        phonemes, stress, vowels = [], "", 0
        for p in re.findall(self.PHONEME_REGEX, pronunciation):
            if p in IPA_STRESS:
                stress = p
            elif p[0] in IPA_VOWELS:
                phonemes.append(stress+p)
                stress = ""
                vowels += 1
            else:
                if p == "tʃ": p = "t͡?ʃ"
                elif p == "dʒ": p = "d͡?ʒ"
                phonemes.append(p)
        if vowels == 1: 
            try: # autoadd stress mark for monosyllabic words
                i = next(i for i in range(len(phonemes)) if phonemes[i][0] in IPA_VOWELS)
                if phonemes[i] != 'ə':
                    phonemes[i] = 'ˈ' + phonemes[i]
            except StopIteration:
                pass
        return tuple(phonemes)

    def arpabet_to_phonemes(self, pronunciation):
        phonemes = []
        for l in pronunciation.split(" "):
            phoneme = ""
            if l == 'AH0': l = 'AX0' # distinguish ʌ from ə
            if l[-1] in ('0', '1', '2'):
                phoneme += { '0': '', '1': 'ˈ', '2': 'ˌ' }[l[-1]]
                l = l[:-1]
            phoneme += self.ARPABET_TO_IPA[l]
            phonemes.append(phoneme)
        return tuple(phonemes)

    @classmethod
    def _is_vowel(self, phoneme): return phoneme[-1] in IPA_VOWELENDINGS
    
    @classmethod
    def _is_stressed(self, phoneme, secondary=False): return phoneme[0] == 'ˈ' or secondary and phoneme[0] == 'ˌ'
    
    @classmethod
    def _is_consonant(self, phoneme): return phoneme[-1] not in IPA_VOWELENDINGS
    
    # MutableMapping
    
    def __getitem__(self, word):
        """Return the pronunciations of a word in IPA. Syllable boundaries aren't marked and stress marks go before the stressed vowel."""
        return {"".join(pronunciation) for pronunciation in self.pdict[word]}
        
    def __setitem__(self, word, pronunciations):
        """Set pronunciations of a word in IPA. If a single pronunciation is given then it is appended to existing ones."""
        if non_string_iterable(pronunciations):
            self.pdict[word] = { q for p in pronunciations for q in self.ipa_to_phonemes(p) }
        else:
            self.pdict.setdefault(word, set()).update(self.ipa_to_phonemes(pronunciations))
        
    def __delitem__(self, word):
        """Delete all pronunciations of a word."""
        del self.pdict[word]
        
    def __iter__(self):
        return iter(self.pdict)
        
    def __len__(self):
        return len(self.pdict)
        
    def __repr__(self):
        return "<Nouncer: {} entries>".format(len(self))
        
    # rest of API
    
    def pronunciations(self, word_filter=None, pronunciation_filter=None):
        """Generator returning matching pronunciations."""
        def match(pattern, string):
            return True if pattern is None else pattern(string) if callable(pattern) else re.search(pattern, string)
        return ((w, p) for w,ps in self.items() if match(word_filter,w) for p in ps if match(pronunciation_filter, p))
    
    def syllables(self, word, default_counter=None):
        """Number of syllables in a word."""
        try:
            return {"".join(pronunciation) : sum(1 for phoneme in pronunciation if self._is_vowel(phoneme)) for pronunciation in self.pdict[word]}
        except KeyError:
            if default_counter is not None:
                return { "({})".format(word): default_counter(word) }
            raise
       
    @classmethod
    def _rhymeswith(self, phonemes1, phonemes2, identirhyme=False, enjambment=False, multirhyme=False):
        stress1 = first_or_default((i for i in range(len(phonemes1)) if self._is_stressed(phonemes1[i])), 0)
        stress2 = first_or_default((i for i in range(len(phonemes2)) if self._is_stressed(phonemes2[i])), 0)
        same_consonant = stress1==stress2==0 or stress1>0 and stress2>0 and phonemes1[stress1-1]==phonemes2[stress2-1]
        pattern1 = phonemes1[stress1:len(phonemes2)-stress2+stress1 if enjambment else None]
        pattern2 = phonemes2[stress2:]
        if multirhyme:
            def strip_consonants(p):
                lv = first_or_default((i for i in reversed(range(len(p))) if self._is_vowel(p[i])), 0)
                return [x for i,x in enumerate(p) if self._is_vowel(x) or i >= lv]
            pattern1 = strip_consonants(pattern1)
            pattern2 = strip_consonants(pattern2)
        return pattern1 == pattern2 and (not same_consonant or identirhyme)
        
    def rhymes(self, word, identirhyme=False, enjambment=False, multirhyme=False):
        """Rhymes for a word."""
        d = {}
        for p1 in self.pdict[word]:
            for w2, ps2 in self.pdict.items():
                for p2 in ps2:
                    if self._rhymeswith(p1, p2, identirhyme, enjambment, multirhyme):
                        d.setdefault("".join(p1), []).append(w2)
        return d
        
def english_syllables(word):
    """Simple heuristic for the number of syllables in an English word. 91% agreement with CMUDict."""
    pos = ["[aeiouy]+",
           "[^cgj]eo|[^cgst]ia|ii|[^cgstx]io|io$|[^g]iu|[^qg]ua|[^g]uo",
           "^mc|(s|th)ms?$",
           "[aeiouy]ing"]
    neg = ["[aeiouy]n?[^aeiouy]h?e$",
           "[aeiouy]([^aeiouytd]|tc?h)+ed$",
           "[aeiouy]r?[^aeiouycszxh]h?es$",
           "cally$|[^ei]ely$"]
    return sum(len(re.findall(r, word)) for r in pos) - sum(len(re.findall(r, word)) for r in neg)

def wiktionary_to_csv(input, output, language="en", accents=("US", "USA", "GA", "GenAm", None)):
    """Extract IPA pronunciations from wiktionary xml dump."""
    title_regex = re.compile("<title>(.*)</title>")
    ipa_regex_1 = re.compile("{{{{IPA[|]/([^|]+)/[|]lang={lang}}}}}".format(lang=language))
    ipa_regex_2 = re.compile("{{{{IPA[|]lang={lang}[|]/([^|]+)/}}}}".format(lang=language))
    accent_regex = re.compile("{{{{a(ccent)?[|]([^}}]+[|])?({accents})[|}}]".format(accents="|".join(a for a in make_iterable(accents) if a)))
    any_accent_regex = re.compile("{{a(ccent)?[|]")
    match = ValueCache()
    with open(input, "r", encoding="utf-8") as i:
        with open(output, "w", encoding="utf-8") as o:
            for line in i:
                if match.set(re.search(title_regex, line)):
                    title = match.value.group(1)
                elif match.set(re.search(ipa_regex_1, line) or re.search(ipa_regex_2, line)):
                    if accents and not re.search(accent_regex, line) and (None not in accents or re.search(any_accent_regex, line)):
                        continue
                    elif ":" in title:
                        continue
                    for pronunciation in match.value.group(1).split(", "):
                        print("{}\t{}".format(title, pronunciation), file=o)
