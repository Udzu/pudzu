from pudzu.sandbox.unicode import *
from pudzu.sandbox.bamboo import *
from pudzu.charts import *

# cf http://www.cesarkallas.net/arquivos/livros/informatica/unicode/ch06.pdf

try:
    df = pd.read_csv("cache/unicode_data.csv", index_col=0, low_memory=False)
    logger.info("Using cached unicode data")
except:
    df = unicode_data({"Scripts", "emoji-data", "DerivedCoreProperties"})
    df.to_csv("cache/unicode_data.csv")
    
df["Emoji"] = df["emoji-data"].apply(lambda x: not pd.isna(x) and "Emoji" in x)
df["Math"] = df["DerivedCoreProperties"].apply(lambda x: not pd.isna(x) and "Math" in x)
df["Script"] = np.select([~df["Scripts"].isin(["Common", "Inherited"]), df["Emoji"], df["Math"], df["Scripts"] == "Inherited"],
                         [df["Scripts"], "Emoji", "Mathematical_Notation", "Common"],
                         df["Scripts"])

scripts = pd.read_csv("datasets/unicode_scripts.csv", index_col="Name")
scripts["Count"] = df.Script.value_counts()
scripts["Count"] = scripts.Count.fillna(0).astype(int)
scripts["Other"] = scripts.index != "Common"
scripts = scripts.sort_values(["Other", "Count"], ascending=False)

script_types = scripts.reset_index().groupby("Type").agg(tuple)
script_types["Total"] = script_types.Count.apply(sum)
script_types = script_types.sort_values("Total", ascending=False)
counts = script_types.explode_to_columns("Count", append=False)
names = script_types.explode_to_columns("Name", append=False)

TITLE = "Unicode characters per writing script type"
SUBTITLE = f"the {len(df):,} assigned characters in Unicode 12.1, categorised by the type of script they belong to"
FOOTER = f"""*//excludes private use code points, surrogates and non-characters; based on the Script Unicode property, with Common and Inherited values making up the 'shared characters' category, in which Emoji and Math characters correspond to the Emoji and Math properties.//"""

LABEL_RENAME = { "Common": "(other)", "Mathematical_Notation": "Math", "Egyptian_Hieroglyphs": "Hieroglyphs", "Canadian_Aboriginal": "Canadian syllabics" }
TYPE_RENAME = {"logographic": "logographic\nscript", "featural": "featural\nscript",}

def colorfn(c,r,v):
    def bar(sz):
        img = Rectangle(sz,VegaPalette10[r])
        if all(sz): img = img.trim((0,1,0,0)).pad((0,1,0,0),"black")
        return img
    return bar

def clabelfn(c,r,v):
    if v < 800: return None
    label = names.iloc[r,c]
    return LABEL_RENAME.get(label,label)

def rlabelfn(r):
    count = counts.count(axis=1)[r]
    label = TYPE_RENAME.get(counts.index[r], counts.index[r])
    if label == "common": return "shared\ncharacters"
    plural = label[:-1]+"ies" if label.endswith("y") else label+"s"
    return f"{count} {plural}"
    
chart = bar_chart(counts.fillna(0), 100, 1900, type=BarChartType.STACKED,
                  ymax=ceil_significant(counts.fillna(0).sum(axis=1).max(), 3)-1,
                  colors=colorfn,
                  spacing=5, label_font=sans(12), clabels=clabelfn, rlabels=rlabelfn, ylabels="{:,}",
                  ylabel=Image.from_text("# of assigned code points", sans(20), padding=10).transpose(Image.ROTATE_90),
                  grid_interval=5000, tick_interval=1000)

# legend (WIP) (TODO: figure out how to properly handle missing Unicode characters!)

LOGOGRAPHIC = f"""**LOGOGRAPHIC SCRIPTS** ({script_types.Total["logographic"]:,})
The earliest writing scripts used hundreds of symbols to represent different words or concepts. They were never //fully// logographic though: new words were constructed via the //rebus principle//, using characters for their sounds (e.g. writing 'idea' as 'eye'+'dear').

**Han script** 汉字 ({scripts.Count["Han"]:,})
//Chinese characters are used in Chinese, Japanese, and (to a small extent) Korean. Despite the unification of the sometimes visually distinct variants, they make up {scripts.Count["Han"]/len(df):.0%} of all Unicode characters. Functional literacy in Chinese requires knowing around 3,000 characters.//

**Egyptian Hieroglyphs**                    ({scripts.Count["Egyptian_Hieroglyphs"]:,})
//Deciphered in 1820 using the Rosetta Stone, Egyptian Hieroglyphs are (via the Sinaitic abjad) the ancestor of almost every alphabet in use today.//

**Sumero-Akkadian Cuneiform**               ({scripts.Count["Cuneiform"]:,})
//These wedge-shaped marks on clay tablets compete with Egyptian Hieroglyphs for the title of oldest writing.//
"""

SYLLABARY = f"""**SYLLABARIES** ({script_types.Total["syllabary"]:,})
One transition to a purely phonetic script involved using dozens of symbols to represent every possible syllable (typically a consonant + a vowel). These were often derived from simplified logograms.

**Hiragana** ひらがな ({scripts.Count["Hiragana"]:,})
//One of two syllabaries used in Japanese, Hiragana is mostly used to write grammatical and function words. The other, Katakana, is for loanwords or emphasis.//

**Cherokee**                                  ({scripts.Count["Cherokee"]:,})
//Invented in 1821 by Sequoyah and soon adopted by the Cherokee Nation. Many characters look like Latin, but represent unrelated sounds: e.g. 4 spells /se/.//

**Linear B** ({scripts.Count["Linear_B"]:,})
//Deciphered only in 1952, Linear B was the earliest form of written Greek. It succeeded Linear A, a still undeciphered (but probably still syllabic) script.//
"""

ABJAD = f"""**ABJADS** ({script_types.Total["abjad"]:,})
The first alphabets only included signs for consonants, with vowel sounds implied by the phonology (or later indicated with optional markings). Most are written right-to-left, like Egyptian usually was.

**Arabic** اَلْعَرَبِيَّةُ \u200e({scripts.Count["Arabic"]:,})
//Also used for Persian and Urdu, Arabic is the fourth most used script in the world. It is heavily cursive, resulting in multiple presentation forms for each letter.//

**Hebrew** עברית \u200e({scripts.Count["Hebrew"]:,})
//A stylised form of the Aramaic abjad, Hebrew is also used to write Yiddish and Ladino. The first letter, א, is a rare mathematical symbol not from Latin or Greek.//

**Phoenician**                                 \u200e({scripts.Count["Phoenician"]:,})
//An early abjad, and an ancestor Greek, Aramaic, and (through them) most other alphabets. Its ancestor, Proto-Sinaitic, is not yet encoded in Unicode.//
"""

ALPHABET = f"""**ALPHABETS** ({script_types.Total["alphabet"]:,})
Alphabet in the wide sense includes any script that encodes individual sounds (rather than syllables or words). Narrowly, however, it is restricted to those that write consonants and vowels as independent letters.

**Latin** ({scripts.Count["Latin"]:,})
//Latin is by far the most widely used script in the world, used by around 70% of the world (including Chinese pinyin). Its wide usage, by unrelated languages, has resulted in a plethora of diacritics and ligatures.//

**Greek** Ελληνικά ({scripts.Count["Greek"]:,})
//Greek was the first true alphabet, repurposing unused Phoenician consonants as vowels. It is also why most alphabets are written left-to-right, a switch that followed an intermediate alternating 'boustrophedon' phase.//

**Cyrillic** Кириллица ({scripts.Count["Cyrillic"]:,})
//A descendent of Greek, Cyrillic (named after St Cyril) was created in Bulgaria, and is used by both Orthodox Slavic and other Russian-influenced languages.//"""

ABUGIDA = f"""**ABUGIDAS** ({script_types.Total["abugida"]:,})
In the third type of alphabet, syllables consist of an explicit consonant and an optional vowel modifier; the lack of a modifier typically results in a default //inherent// vowel. Most abugidas derive from the Brāhmī script of ancient India, itself based on the Aramaic abjad.

**Devanagari** देवनागरी ({scripts.Count["Devanagari"]:,})
//The third most used script in the world, Devanagari ('divine town script') is used by many Indian languages, including Hindi, Punjabi, Marathi and Nepali.//

**Thai** อักษรไทย ({scripts.Count["Thai"]:,})
//The spread of Buddhism brought the Southern Brahmic scripts (aka Tamil-Brahmi) to South East Asia, where they evolved further. Unlike Devenagari (and English), Thai doesn't use spaces to separate words.//

**Geʽez**          ({scripts.Count["Ethiopic"]:,})
//Geʽez (or Ethiopic) is one of the few alphabets not derived from Phoenician: it instead comes from a sister script, Ancient South Arabian. It is used to write a number of languages, including Amharic and Tigrinya.//
"""

SEMISYLLABARY = f"""**SEMI-SYLLABARIES** ({script_types.Total["semi-syllabary"]:,})
A small number of scripts behaves partly as an alphabet and partly as a syllabary. These include the Paleohispanic scripts of ancient Spain (not yet encoded in Unicode) as well as the following.

**Bopomofo** ㄅㄆㄇㄈ ({scripts.Count["Bopomofo"]:,})
//While China uses Latin-based pinyin to transliterate Chinese, Taiwan uses Bopomofo (aka Zhuyin). It has characters for initial consonants (onsets) and syllable ends (rimes): e.g. kan ㄎㄢ is spelled k+an.//

**Bamum** ({scripts.Count["Bamum"]:,})
//Created by King Njoya of Cameroon, Bamum evolved from a pictographic system to a semi-syllabary in just 14 years. The script died out after French colonisation.//

**Old Persian Cuneiform**                               ({scripts.Count["Old_Persian"]:,})
//Invented during the reign of Darius I, this semi-syllabary was only loosely inspired by Sumero-Akkadian Cuneiform, which it superficially resembles.//
"""

FEATURAL = f"""**FEATURAL SCRIPTS** ({script_types.Total["featural"]:,})
A featural script represents even finer detail than an alphabet, in that its symbols are not arbitrary but attempt to encode phonological features of the sounds they represent. The symbols themselves may be combined into alphabetic letters or syllabic blocks. 

**Hangul** 한글 ({scripts.Count["Hangul"]:,})
//The Korean alphabet's 28 letters (jamo) mimic the shape of the speaker's mouth. Letters are written in syllabic blocks, so that ㅎㅏㄴㄱㅡㄹ is written as 한글. The huge number of possible syllables explains the number of assigned characters, though it's also possible to write Hangul by directly combining jamo.//

**Canadian syllabics**                            ({scripts.Count["Canadian_Aboriginal"]:,})
//A family of abugidas used to write indigenous Canadian languages. Vowels are indicated by changing the orientation of consonants (or by adding dots or dashes): e.g. ∧ pi, ∨ pe, < pa and > po.//

**SignWriting** ({scripts.Count["SignWriting"]:,})
Japanese writing Japanese writing Japanese writing Japanese writing. Japanese writing Japanese writing Japanese writing Japanese writing.
"""

COMMON = f"""**SHARED CHARACTERS** ({script_types.Total["common"]:,})
Writing script writing script writing script writing script writing script writing script.

**Emoji** 😂 ({scripts.Count["Emoji"]:,})
Japanese writing Japanese writing Japanese writing Japanese writing. Japanese writing Japanese writing Japanese writing Japanese writing.

**Mathematical Notation** ∫𝑑𝜏(𝜖𝐸²+𝜇𝐻²) ({scripts.Count["Mathematical_Notation"]:,})
Japanese writing Japanese writing Japanese writing Japanese writing. Japanese writing Japanese writing Japanese writing Japanese writing.
"""

def color(script_type): return VegaPalette10[np.where(script_types.index==script_type)[0][0]]
arialu = partial(font, "fonts/arialu")

logographic_legend = Image.from_markup(LOGOGRAPHIC, partial(arialu, 14), max_width=350, fg=color("logographic"), bg="white")
syllabary_legend = Image.from_markup(SYLLABARY, partial(arialu, 14), max_width=350, fg=color("syllabary"), bg="white")
abjad_legend = Image.from_markup(ABJAD, partial(arialu, 14), max_width=350, fg=color("abjad"), bg="white")
alphabet_legend = Image.from_markup(ALPHABET, partial(arialu, 14), max_width=350, fg=color("alphabet"), bg="white")
abugida_legend = Image.from_markup(ABUGIDA, partial(arialu, 14), max_width=350, fg=color("abugida"), bg="white")
semisyllabary_legend = Image.from_markup(SEMISYLLABARY, partial(arialu, 14), max_width=350, fg=color("semi-syllabary"), bg="white")
featural_legend = Image.from_markup(FEATURAL, partial(arialu, 14), max_width=350, fg=color("featural"), bg="white")
common_legend = Image.from_markup(COMMON, partial(arialu, 14), max_width=350, fg=color("common"), bg="white")

logographic_legend.place(Image.open("text/Egyptian.png"), align=0, padding=(155,250), copy=False) # 𓂋𓏤𓈖𓆎𓅓𓏏𓊖
logographic_legend.place(Image.open("text/Cuneiform.png"), align=0, padding=(200,340), copy=False) # 𒅴𒂠
syllabary_legend.place(Image.open("text/Cherokee.png"), align=0, padding=(70,196), copy=False) # ᏣᎳᎩ ᎦᏬᏂᎯᏍᏗ
abjad_legend.place(Image.open("text/Phoenician.png"), align=0, padding=(85,287), copy=False) # 𐤃𐤁𐤓𐤉𐤌 𐤊𐤍𐤏𐤍𐤉𐤌
abugida_legend.place(Image.open("text/Geez.png"), align=0, padding=(40,322), copy=False) # ግዕዝ
semisyllabary_legend.place(Image.open("text/Persian.png"), align=0, padding=(158,304), copy=False) # 𐎧𐏁𐎠𐎹𐎰𐎡𐎹
featural_legend.place(Image.open("text/Aboriginal.png"), align=0, padding=(135,268), copy=False) # ᖃᓂᐅᔮᖅᐸᐃᑦ

left_legend = Image.from_column([logographic_legend, syllabary_legend, abjad_legend, alphabet_legend], xalign=0, padding=(0,0,0,20))
right_legend = Image.from_column([abugida_legend, semisyllabary_legend, featural_legend, common_legend], xalign=0, padding=(0,0,0,20))
legend = Image.from_row([left_legend, right_legend], yalign=0, padding=(15,0)).remove_transparency("white")

chart = chart.place(legend, align=0, padding=(230,20))

# addendum

SCRIPT_ORIGINS = {
    'China': ['Bopomofo', 'Han', 'Lisu', 'Miao', 'New_Tai_Lue', 'Nushu', 'Tangut', 'Tai_Le', 'Yi'],
    'Japan': ['Hiragana', 'Katakana'],
    'Korea': ['Hangul'],
    'Mongolia': ['Mongolian', 'Soyombo', 'Zanabazar_Square'],
    'Tibet': ['Phags_Pa', 'Tibetan']
}
ASIAN_SCRIPTS = sorted(script for scripts in SCRIPT_ORIGINS.values() for script in scripts)
scripts["Asian"] = scripts.index.isin(ASIAN_SCRIPTS)
asian_counts = scripts[scripts.Type != "common"].groupby("Asian").sum().sort_values("Count", ascending=False)
asian_chart = bar_chart(asian_counts[["Count"]].transpose(), 20, chart.width-200, type=BarChartType.STACKED_PERCENTAGE, horizontal=True,
                     label_font=sans(12), grid_interval=0.1, rlabels=None, colors=[VegaPalette10.RED, VegaPalette10.BLUE],
                     clabels=lambda c: [f"{int(asian_counts.Other[True])} East Asian scripts ({asian_counts.Count[True]:,} characters)", 
                                        f"{int(asian_counts.Other[False])} other scripts"][c]).pad((0,0,0,10), "white")
script_list = ", ".join(x.replace("_"," ") for x in ASIAN_SCRIPTS)
ADDENDUM = f"**BONUS FACT**: the 17 East Asian scripts ({script_list}) between them contain 86% of all single-script characters:"
                                        
# title, etc

title = Image.from_text_justified(TITLE.upper(), chart.width-50, 80, partial(sans, bold=True), bg="white", padding=(0,5))
subtitle = Image.from_text_justified(SUBTITLE, chart.width-100, 40, partial(sans, italics=True), bg="white", padding=(0,5,0,20))
footer = Image.from_markup(FOOTER, partial(sans, 14), max_width=chart.width-100, align="left", beard_line=True, bg="white", padding=(0,20,0,10))
addendum = Image.from_markup(ADDENDUM, partial(sans, 14), max_width=chart.width-100, align="left", beard_line=True, bg="white", padding=(0,10,0,10))
img = Image.from_column([title, subtitle, chart, footer], bg="white")
img.save("output/unicode_scripts.png")

                      
# TODO: colors, labels (17 East Asian scripts / 133 others)
