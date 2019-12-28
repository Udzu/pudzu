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

LABEL_RENAME = { "Common": "(other)", "Mathematical_Notation": "Math", "Egyptian_Hieroglyphs": "Hieroglyphs" }
TYPE_RENAME = {"logographic": "logographic\nscript", "featural": "featural\nscript",}

def colorfn(c,r,v):
    def bar(sz):
        img = Rectangle(sz,VegaPalette10[r])
        if all(sz): img = img.trim((0,1,0,0)).pad((0,1,0,0),"black")
        return img
    return bar

def clabelfn(c,r,v):
    if v < 1000: return None
    label = names.iloc[r,c]
    return LABEL_RENAME.get(label,label)

def rlabelfn(r):
    count = counts.count(axis=1)[r]
    label = TYPE_RENAME.get(counts.index[r], counts.index[r])
    if label == "common": return "shared\ncharacters"
    plural = label[:-1]+"ies" if label.endswith("y") else label+"s"
    return f"{count} {plural}"
    
chart = bar_chart(counts.fillna(0), 100, 1200, type=BarChartType.STACKED,
                  ymax=ceil_significant(counts.fillna(0).sum(axis=1).max(), 3)-1,
                  colors=colorfn,
                  spacing=5, label_font=sans(12), clabels=clabelfn, rlabels=rlabelfn, ylabels="{:,}",
                  ylabel=Image.from_text("# of assigned code points", sans(20), padding=10).transpose(Image.ROTATE_90),
                  grid_interval=5000, tick_interval=1000)

# legend (WIP) (TODO: figure out how to properly handle missing Unicode characters!)


LOGOGRAPHIC = f"""**LOGOGRAPHIC SCRIPTS** ({script_types.Total["logographic"]:,})
The earliest scripts were formed of hundreds of symbols representing different words or concepts. Full writing systems were never fully logographic; new words were written using phonetic with semantic.

**Chinese characters (Han)** 汉字 ({scripts.Count["Han"]:,})
Chinese characters are used to write Chinese and Japanese. Alone make up. 8000 Needed for literacy.

**Egyptian Hieroglyphs**                    ({scripts.Count["Egyptian_Hieroglyphs"]:,})
Deciphered in 1820 with aid of, consist of consonant. Still don't know vowels. Via proto sinaitic parent of most writing systems used today. No support for quadrat grouping. 

**Cuneiform**               ({scripts.Count["Cuneiform"]:,})
Wedge shaped marks made on clay tablets, possibly oldest script.
"""

SYLLABARY = f"""**SYLLABARIES** ({script_types.Total["syllabary"]:,})
These have one.

**Hiragana** ひらがな ({scripts.Count["Hiragana"]:,})
Japanese writing Japanese writing Japanese writing Japanese writing.

**Cherokee**                                    ({scripts.Count["Cherokee"]:,})
Sequoia

**Linear B** ({scripts.Count["Linear_B"]:,})
Greek
"""

SEMISYLLABARY = f"""**SEMI-SYLLABARIES** ({script_types.Total["semi-syllabary"]:,})
Blah di blah."""

def color(script_type): return VegaPalette10[np.where(script_types.index==script_type)[0][0]]
arialu = partial(font, "fonts/arialu")

logographic_legend = Image.from_markup(LOGOGRAPHIC, partial(arialu, 14), max_width=350, fg=color("logographic"), bg="white")
logographic_legend.place(Image.open("text/Egyptian.png"), align=0, padding=(155,175), copy=False)
logographic_legend.place(Image.open("text/Cuneiform.png"), align=0, padding=(75,285), copy=False)

syllabary_legend = Image.from_markup(SYLLABARY, partial(arialu, 14), max_width=350, fg=color("syllabary"), bg="white")
syllabary_legend.place(Image.open("text/Cherokee.png"), align=0, padding=(70,110), copy=False)

semisyllabary_legend = Image.from_markup(SEMISYLLABARY, partial(arialu, 14), max_width=350, fg=color("semi-syllabary"), bg="white")

left_legend = Image.from_column([logographic_legend, syllabary_legend], xalign=0, padding=(0,0,0,20))
right_legend = Image.from_column([semisyllabary_legend], xalign=0, padding=(0,0,0,20))
legend = Image.from_row([left_legend, right_legend], yalign=0, padding=(20,0)).remove_transparency("white")

chart = chart.place(legend, align=0, padding=(250,20))

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
