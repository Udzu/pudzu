from pudzu.sandbox.unicode import *

# cf http://www.cesarkallas.net/arquivos/livros/informatica/unicode/ch06.pdf

df = unicode_data({"Scripts", "emoji-data", "DerivedCoreProperties"})
df["Emoji"] = df["emoji-data"].apply(lambda x: not pd.isna(x) and "Emoji" in x)
df["Math"] = df["DerivedCoreProperties"].apply(lambda x: not pd.isna(x) and "Math" in x)
df["Script"] = np.select([df["Scripts"] != "Common", df["Emoji"], df["Math"]],
                         [df["Scripts"], "Emoji", "Mathematical_Notation"],
                         df["Scripts"])

scripts = pd.read_csv("datasets/unicode_scripts.csv", index_col="Name")
scripts["Counts"] = df.Script.value_counts()
scripts["Number"] = 1

counts_by_type = scripts.groupby("Type").sum().sort_values("Count", ascending=False)

ASIAN_SCRIPTS = {
    'China': ['Bopomofo', 'Han', 'Lisu', 'Miao', 'New_Tai_Lue', 'Nushu', 'Tangut', 'Tai_Le', 'Yi'],
    'Japan': ['Hiragana', 'Katakana'],
    'Korea': ['Hangul'],
    'Mongolia': ['Mongolian', 'Soyombo', 'Zanabazar_Square'],
    'Tibet': ['Phags_Pa', 'Tibetan']
}

