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
scripts = scripts.sort_values("Count", ascending=False)

script_types = scripts.reset_index().groupby("Type").agg(tuple)
script_types = script_types.reindex(["abjad", "alphabet", "abugida", "semi-syllabary", "syllabary", "logographic", "featural", "common"])
counts = script_types.explode_to_columns("Count", append=False)
names = script_types.explode_to_columns("Name", append=False)

LABEL_RENAME = { "Common": "Other\nCommon", "Mathematical_Notation": "Math", "Egyptian_Hieroglyphs": "Hieroglyphs" }

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
    
chart = bar_chart(counts.fillna(0), 100, 1200, type=BarChartType.STACKED,
                  ymax=counts.sum(axis=1).max(),
                  colors=colorfn,
                  spacing=5, label_font=arial(12), clabels=clabelfn,
                  # ylabels=lambda v: str(v)[0:2]+" million" if v > 0 else "0",
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
