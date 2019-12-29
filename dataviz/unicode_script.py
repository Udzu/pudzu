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
# script_types = script_types.reindex(["logographic", "syllabary", "abjad", "alphabet", "semi-syllabary", "abugida", "featural", "common"])
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
    
chart = bar_chart(counts.fillna(0), 100, 1800, type=BarChartType.STACKED,
                  ymax=ceil_significant(counts.fillna(0).sum(axis=1).max(), 3)-1,
                  colors=colorfn,
                  spacing=5, label_font=sans(12), clabels=clabelfn, rlabels=rlabelfn, ylabels="{:,}",
                  ylabel=Image.from_text("# of assigned code points", sans(20), padding=10).transpose(Image.ROTATE_90),
                  grid_interval=5000, tick_interval=1000)

# legend (WIP) (TODO: figure out how to properly handle missing Unicode characters!)


LOGOGRAPHIC = f"""**LOGOGRAPHIC SCRIPTS** ({script_types.Total["logographic"]:,})
The earliest writing scripts used hundreds of symbols to represent different words or concepts. They were never //fully// logographic though: new words were constructed via the //rebus principle//, using characters for their sounds (e.g. writing 'idea' as 'eye'+'dear').

**Han script** 汉字 ({scripts.Count["Han"]:,})
//Chinese characters are used to write Chinese, Japanese, and (to a lesser extent) Korean. Despite the unification of the sometimes visually distinct characters used in those languages, they alone make up {scripts.Count["Han"]/len(df):.0%} of all Unicode characters. Functional literacy in Chinese requires knowing around 3,000 characters.//

**Egyptian Hieroglyphs**                    ({scripts.Count["Egyptian_Hieroglyphs"]:,})
//Deciphered in 1820 using the Rosetta Stone, Egyptian Hieroglyphs are (via the Sinaitic abjad) the direct ancestor of almost every alphabet in use today.//

**Sumero-Akkadian Cuneiform**               ({scripts.Count["Cuneiform"]:,})
//These wedge-shaped marks on clay tablets compete with Egyptian Hieroglyphs for the title of oldest writing.//
"""

SYLLABARY = f"""**SYLLABARIES** ({script_types.Total["syllabary"]:,})
Later scripts used ...dozens...syllabels..., often derived from simplified logograms.

**Hiragana** ひらがな ({scripts.Count["Hiragana"]:,})
//One of two syllabaries used in Japanese, Hiragana is mostly used to write grammatical and function words. The other, Katakana, is for loanwords or emphasis.//

**Cherokee**                                  ({scripts.Count["Cherokee"]:,})
//Invented in 1821 by Sequoyah and soon adopted by the Cherokee Nation. Many characters look like Latin, but represent unrelated sounds: e.g. 4 spells /se/.//

**Linear B** ({scripts.Count["Linear_B"]:,})
//Deciphered only in 1952, Linear B was the earliest form of written Greek. It succeeded Linear A, a still undeciphered (though likely syllabic) script.//
"""

ABJAD = f"""**ABJADS** ({script_types.Total["abjad"]:,})
Writing script writing script writing script writing script writing script writing script.

**Arabic** اَلْعَرَبِيَّةُ \u200e({scripts.Count["Arabic"]:,})
Japanese writing Japanese writing Japanese writing Japanese writing.

**Hebrew** עברית \u200e({scripts.Count["Hebrew"]:,})
Japanese writing Japanese writing Japanese writing Japanese writing.

**Phoenician**                                    \u200e({scripts.Count["Phoenician"]:,})
Japanese writing Japanese writing Japanese writing Japanese writing.
"""

ALPHABET = f"""**ALPHABETS** ({script_types.Total["alphabet"]:,})
Writing script writing script writing script writing script writing script writing script.

**Latin** ({scripts.Count["Latin"]:,})
Japanese writing Japanese writing Japanese writing Japanese writing.

**Greek** Ελληνικά ({scripts.Count["Greek"]:,})
Japanese writing Japanese writing Japanese writing Japanese writing.

**Cyrillic** Кириллица ({scripts.Count["Cyrillic"]:,})
Japanese writing Japanese writing Japanese writing Japanese writing.
"""

SEMISYLLABARY = f"""**SEMI-SYLLABARIES** ({script_types.Total["semi-syllabary"]:,})
Writing script writing script writing script writing script writing script writing script.

**Bopomofo** ㄅㄆㄇㄈ ({scripts.Count["Bopomofo"]:,})
Japanese writing Japanese writing Japanese writing Japanese writing.

**Bamum** ({scripts.Count["Bamum"]:,})
Japanese writing Japanese writing Japanese writing Japanese writing.

**Old Persian** ({scripts.Count["Old_Persian"]:,})
Japanese writing Japanese writing Japanese writing Japanese writing.
"""

ABUGIDA = f"""**ABUGIDAS** ({script_types.Total["abugida"]:,})
Writing script writing script writing script writing script writing script writing script.

**Devanagari** देवनागरी ({scripts.Count["Devanagari"]:,})
Japanese writing Japanese writing Japanese writing Japanese writing.

**Thai** อักษรไทย ({scripts.Count["Thai"]:,})
Japanese writing Japanese writing Japanese writing Japanese writing.

**Ge'ez** ግዕዝ ({scripts.Count["Ethiopic"]:,})
Japanese writing Japanese writing Japanese writing Japanese writing.
"""

FEATURAL = f"""**FEATURAL SCRIPTS** ({script_types.Total["featural"]:,})
Writing script writing script writing script writing script writing script writing script.

**Hangul** 한글 ({scripts.Count["Hangul"]:,})
Japanese writing Japanese writing Japanese writing Japanese writing.

**Canadian Aboriginal syllabics** ᖃᓂᐅᔮᖅᐸᐃᑦ ({scripts.Count["Canadian_Aboriginal"]:,})
Japanese writing Japanese writing Japanese writing Japanese writing.

**SignWriting** ግዕዝ ({scripts.Count["SignWriting"]:,})
Japanese writing Japanese writing Japanese writing Japanese writing.
"""

COMMON = f"""**SHARED CHARACTERS** ({script_types.Total["featural"]:,})
Writing script writing script writing script writing script writing script writing script.

**Emoji** 😂 ({scripts.Count["Emoji"]:,})
Japanese writing Japanese writing Japanese writing Japanese writing.

**Mathematical Notation** ({scripts.Count["Mathematical_Notation"]:,})
Japanese writing Japanese writing Japanese writing Japanese writing.

**Other shared characters** ({scripts.Count["Common"]:,})
Japanese writing Japanese writing Japanese writing Japanese writing.
"""

def color(script_type): return VegaPalette10[np.where(script_types.index==script_type)[0][0]]
arialu = partial(font, "fonts/arialu")

logographic_legend = Image.from_markup(LOGOGRAPHIC, partial(arialu, 14), max_width=350, fg=color("logographic"), bg="white")
syllabary_legend = Image.from_markup(SYLLABARY, partial(arialu, 14), max_width=350, fg=color("syllabary"), bg="white")
abjad_legend = Image.from_markup(ABJAD, partial(arialu, 14), max_width=350, fg=color("abjad"), bg="white")
alphabet_legend = Image.from_markup(ALPHABET, partial(arialu, 14), max_width=350, fg=color("alphabet"), bg="white")
semisyllabary_legend = Image.from_markup(SEMISYLLABARY, partial(arialu, 14), max_width=350, fg=color("semi-syllabary"), bg="white")
abugida_legend = Image.from_markup(ABUGIDA, partial(arialu, 14), max_width=350, fg=color("abugida"), bg="white")
featural_legend = Image.from_markup(FEATURAL, partial(arialu, 14), max_width=350, fg=color("featural"), bg="white")
common_legend = Image.from_markup(COMMON, partial(arialu, 14), max_width=350, fg=color("common"), bg="white")

logographic_legend.place(Image.open("text/Egyptian.png"), align=0, padding=(155,267), copy=False) # 𓂋𓏤𓈖𓆎𓅓𓏏𓊖
logographic_legend.place(Image.open("text/Cuneiform.png"), align=0, padding=(200,358), copy=False) # 𒅴𒂠
syllabary_legend.place(Image.open("text/Cherokee.png"), align=0, padding=(70,160), copy=False) # ᏣᎳᎩ ᎦᏬᏂᎯᏍᏗ
abjad_legend.place(Image.open("text/Phoenician.png"), align=0, padding=(80,190), copy=False) # 𐤃𐤁𐤓𐤉𐤌 𐤊𐤍𐤏𐤍𐤉𐤌

left_legend = Image.from_column([logographic_legend, syllabary_legend, abjad_legend, alphabet_legend], xalign=0, padding=(0,0,0,20))
right_legend = Image.from_column([semisyllabary_legend, abugida_legend, featural_legend, common_legend], xalign=0, padding=(0,0,0,20))
legend = Image.from_row([left_legend, right_legend], yalign=0, padding=(15,0)).remove_transparency("white")

chart = chart.place(legend, align=0, padding=(230,20))

# title, etc

title = Image.from_text_justified(TITLE.upper(), chart.width-50, 80, partial(sans, bold=True), bg="white", padding=(0,5))
subtitle = Image.from_text_justified(SUBTITLE, chart.width-100, 40, partial(sans, italics=True), bg="white", padding=(0,5,0,20))
footer = Image.from_markup(FOOTER, partial(sans, 14), max_width=chart.width-100, align="left", beard_line=True, bg="white", padding=(0,20,0,10))
img = Image.from_column([title, subtitle, chart, footer], bg="white")
img.save("output/unicode_scripts.png")

# SCRIPT_ORIGINS = {
    # 'China': ['Bopomofo', 'Han', 'Lisu', 'Miao', 'New_Tai_Lue', 'Nushu', 'Tangut', 'Tai_Le', 'Yi'],
    # 'Japan': ['Hiragana', 'Katakana'],
    # 'Korea': ['Hangul'],
    # 'Mongolia': ['Mongolian', 'Soyombo', 'Zanabazar_Square'],
    # 'Tibet': ['Phags_Pa', 'Tibetan']
# }
# ASIAN_SCRIPTS = [ script for scripts in SCRIPT_ORIGINS.values() for script in scripts ]
