from pudzu.sandbox.unicode import *
from pudzu.sandbox.bamboo import *
from pudzu.charts import *

# cf http://www.cesarkallas.net/arquivos/livros/informatica/unicode/ch06.pdf

df = unicode_data({"Scripts", "emoji-data", "DerivedCoreProperties"})
df["Emoji"] = df["emoji-data"].apply(lambda x: not pd.isna(x) and "Emoji" in x)
df["Math"] = df["DerivedCoreProperties"].apply(lambda x: not pd.isna(x) and "Math" in x)
df["Script"] = np.select([~df["Scripts"].isin(["Common", "Inherited"]), df["Emoji"], df["Math"], df["Scripts"] == "Inherited"],
                         [df["Scripts"], "Emoji", "Mathematical_Notation", "Common"],
                         df["Scripts"])

scripts = pd.read_csv("datasets/unicode_scripts.csv", index_col="Name")
scripts["Count"] = df.Script.value_counts()
scripts["Other"] = scripts.index != "Common"
scripts = scripts.fillna(0).sort_values(["Other", "Count"], ascending=False)

script_types = scripts.reset_index().groupby("Type").agg(tuple)
script_types["Total"] = script_types.Count.apply(sum)
# script_types = script_types.reindex(["logographic", "syllabary", "abjad", "alphabet", "semi-syllabary", "abugida", "featural", "common"])
script_types = script_types.sort_values("Total", ascending=False)
counts = script_types.explode_to_columns("Count", append=False)
names = script_types.explode_to_columns("Name", append=False)

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
                  spacing=5, label_font=arial(12), clabels=clabelfn, rlabels=rlabelfn, ylabels="{:,}",
                  ylabel=Image.from_text("# of assigned codepoints", arial(20), padding=10).transpose(Image.ROTATE_90),
                  grid_interval=5000, tick_interval=1000)

# TODO: palette, top script examples, % asian?

# SCRIPT_ORIGINS = {
    # 'China': ['Bopomofo', 'Han', 'Lisu', 'Miao', 'New_Tai_Lue', 'Nushu', 'Tangut', 'Tai_Le', 'Yi'],
    # 'Japan': ['Hiragana', 'Katakana'],
    # 'Korea': ['Hangul'],
    # 'Mongolia': ['Mongolian', 'Soyombo', 'Zanabazar_Square'],
    # 'Tibet': ['Phags_Pa', 'Tibetan']
# }
# ASIAN_SCRIPTS = [ script for scripts in SCRIPT_ORIGINS.values() for script in scripts ]
