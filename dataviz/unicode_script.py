from pudzu.sandbox.unicode import *
from pudzu.sandbox.bamboo import *
from pudzu.charts import *

# cf http://www.cesarkallas.net/arquivos/livros/informatica/unicode/ch06.pdf

df = unicode_data({"Scripts", "emoji-data", "DerivedCoreProperties"})
df["Emoji"] = df["emoji-data"].apply(lambda x: not pd.isna(x) and "Emoji" in x)
df["Math"] = df["DerivedCoreProperties"].apply(lambda x: not pd.isna(x) and "Math" in x)
df["Script"] = np.select([df["Scripts"] != "Common", df["Emoji"], df["Math"]],
                         [df["Scripts"], "Emoji", "Mathematical_Notation"],
                         df["Scripts"])

scripts = pd.read_csv("datasets/unicode_scripts.csv", index_col="Name")
scripts["Count"] = df.Script.value_counts()
scripts = scripts.sort_values("Count")

script_types = scripts.reset_index().groupby("Type").agg(tuple)
script_types = script_types.reindex(["abjad", "alphabet", "abugida", "semi-syllabary", "syllabary", "logographic", "featural", "other"])
counts = script_types.explode_to_columns("Count", append=False)
names = script_types.explode_to_columns("Name", append=False)

# SCRIPT_ORIGINS = {
    # 'China': ['Bopomofo', 'Han', 'Lisu', 'Miao', 'New_Tai_Lue', 'Nushu', 'Tangut', 'Tai_Le', 'Yi'],
    # 'Japan': ['Hiragana', 'Katakana'],
    # 'Korea': ['Hangul'],
    # 'Mongolia': ['Mongolian', 'Soyombo', 'Zanabazar_Square'],
    # 'Tibet': ['Phags_Pa', 'Tibetan']
# }
# ASIAN_SCRIPTS = [ script for scripts in SCRIPT_ORIGINS.values() for script in scripts ]
