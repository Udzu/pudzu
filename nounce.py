import re
from utils import *

# Pronouncing dictionary class

IPA_VOWELS = "ɔɑiuɛɪʊʌəæeaoyʏø"
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
                    self.pdict.setdefault(m.group(1), []).append(self.arpabet_to_phonemes(m.group(2)))
        
    def import_wiktionary(self, filename):
        raise NotImplementedError
        
    # TODO: basic prototype, need work!
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
                
        # add stress mark for monosyllabic words if there isn't one already
        if vowels == 1:
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

    # API
    
    def __getitem__(self, word):
        """Return the pronunciation of a word in IPA. Syllable boundaries aren't marked and stress marks go before the stressed vowel."""
        return ["".join(pronunciation) for pronunciation in self.pdict[word]]
        
    def __setitem__(self, word, pronunciation):
        self.pdict[word] = self.ipa_to_phonemes(pronunciation)
        
    def syllables(self, word):
        return [sum(1 for phoneme in pronunciation if phoneme[-1] in IPA_VOWELS + "ː̯̩") for pronunciation in self.pdict[word]]
        
    def rhymes(self, word):
        raise NotImplementedError
        
pd = Nouncer()
pd.import_cmudict("corpora/cmudict.0.7a")
