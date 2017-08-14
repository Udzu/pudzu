import re
from utils import *

# Pronouncing dictionary class

IPA_VOWELS = "ɔɑiuɛɪʊʌəæeaoyʏøɝɚ"
IPA_STRESS = "ˈˌ"

class Nouncer(object):

    def __init__(self, filename=None, normalize=str.lower):
        self.pdict = CaseInsensitiveDict(normalize=normalize)
        if filename is not None:
            with open(filename, "r", encoding="utf-8") as f:
                for entry in f:
                    m = re.match("(.*)\t(.*)", entry)
                    if m:
                        self.pdict.setdefault(m.group(1), []).append(m.group(2).split(" "))
        
    def save(self, filename):
        with open(filename, 'w', encoding='utf-8') as f:
            for word in sorted(self.pdict.keys()):
                for pronunciation in self.pdict[word]:
                    print("{}\t{}".format(word, " ".join(pronunciation)), file=f)
     
    def import_cmudict(self, filename):
        with open(filename, "r", encoding="latin-1") as f:
            for entry in f:
                m = re.match("([^(]*)(?:[(][0-9][)])?  (.*)", entry)
                if m:
                    self.pdict.setdefault(m.group(1).lower(), []).append(self.arpabet_to_phonemes(m.group(2)))
        
    def import_wiktionary(self, filename):
        raise NotImplementedError
        
    # TODO: basic prototype, needs work!
    def ipa_to_phonemes(self, pronunciation):
        phonemes, stress, vowels = [], "", 0
        for p in re.findall(self.UNIT_PATTERN, pronunciation):
            if p in IPA_STRESS:
                stress = p
            elif p[0] in IPA_VOWELS:
                phonemes.append(stress+p)
                stress = ""
                vowels += 1
            else:
                phonemes.append(p)
        if vowels == 1: # autoadd stress mark for monosyllabic words
            try:
                i = next(i for i in range(len(phonemes)) if phonemes[i][0] in IPA_VOWELS)
                if phonemes[i] != 'ə':
                    phonemes[i] = 'ˈ' + phonemes[i]
            except StopIteration:
                pass
        return phonemes
        
    UNIT_PATTERN = re.compile("([{stress}]|(?:[{vowel}][ː]?[ʊɪə]?[̯]?)|.)[.]?".format(stress=IPA_STRESS, vowel=IPA_VOWELS))

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
        return phonemes
        
    ARPABET_TO_IPA = { 'AO': 'ɔ', 'AA': 'ɑ', 'IY': 'i', 'UW': 'u', 'EH': 'ɛ', 'IH': 'ɪ', 'UH': 'ʊ', 'AH': 'ʌ', 'AX': 'ə', 'AE': 'æ',
                       'EY': 'eɪ', 'AY': 'aɪ', 'OW': 'oʊ', 'AW': 'aʊ', 'OY': 'ɔɪ', 'ER': 'ɝ', 'AXR': 'ɚ',
                       'P': 'p', 'B': 'b', 'T': 't', 'D': 'd', 'K': 'k', 'G': 'ɡ', 'CH': 'tʃ', 'JH': 'dʒ', 'F': 'f', 'V': 'v',
                       'TH': 'θ', 'DH': 'ð', 'S': 's', 'Z': 'z', 'SH': 'ʃ', 'ZH': 'ʒ', 'HH': 'h', 'M': 'm', 'EM': 'm̩',
                       'N': 'n', 'EN': 'n̩', 'NG': 'ŋ', 'ENG': 'ŋ̍', 'L': 'l', 'EL': 'ɫ̩', 'R': 'r', 'DX': 'ɾ', 'NX': 'ɾ̃',
                       'Y': 'j', 'W': 'w', 'Q': 'ʔ' }

    @classmethod
    def _is_vowel(self, phoneme): return phoneme[-1] in self.IPA_VOWELENDINGS
    
    @classmethod
    def _is_stressed(self, phoneme, secondary=False): return phoneme[0] == 'ˈ' or secondary and phoneme[0] == 'ˌ'
    
    @classmethod
    def _is_consonant(self, phoneme): return phoneme[-1] not in self.IPA_VOWELENDINGS
    
    IPA_VOWELENDINGS = IPA_VOWELS + "ː̯̩"
    
    # API
    
    def __getitem__(self, word):
        """Return the pronunciation of a word in IPA. Syllable boundaries aren't marked and stress marks go before the stressed vowel."""
        return ["".join(pronunciation) for pronunciation in self.pdict[word]]
        
    def __setitem__(self, word, pronunciation):
        self.pdict[word] = self.ipa_to_phonemes(pronunciation)
        
    def syllables(self, word):
        return [sum(1 for phoneme in pronunciation if self._is_vowel(phoneme)) for pronunciation in self.pdict[word]]
       
    @classmethod
    def _rhymeswith(self, phonemes1, phonemes2, identirhyme=False, enjambment=False, multirhyme=False):
        stress1 = first_or_default((i for i in range(len(phonemes1)) if self._is_stressed(phonemes1[i])), 0)
        stress2 = first_or_default((i for i in range(len(phonemes2)) if self._is_stressed(phonemes2[i])), 0)
        same_consonant = stress1==stress2==0 or stress1>0 and stress2>0 and phonemes1[stress1-1]==phonemes2[stress2-1]
        pattern1 = phonemes1[stress1:]
        pattern2 = phonemes2[stress2:len(phonemes1)-stress1+stress2 if enjambment else None]
        if multirhyme:
            def strip_consonants(p):
                lv = first_or_default((i for i in reversed(range(len(p))) if self._is_vowel(p[i])), 0)
                return [x for i,x in enumerate(p) if self._is_vowel(x) or i >= lv]
            pattern1 = strip_consonants(pattern1)
            pattern2 = strip_consonants(pattern2)
        return pattern1 == pattern2 and (not same_consonant or identirhyme)
        
    def rhymes(self, word, identirhyme=False, enjambment=False, multirhyme=False):
        d = {}
        for p1 in self.pdict[word]:
            for w2, ps2 in self.pdict.items():
                for p2 in ps2:
                    if self._rhymeswith(p1, p2, identirhyme, enjambment, multirhyme):
                        d.setdefault("".join(p1), []).append(w2)
        return d
        
pd = Nouncer("corpora/nouncedict")

