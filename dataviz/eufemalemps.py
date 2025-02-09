from pudzu.pillar import *
from pudzu.charts import *
from pudzu.utils import *

"""
Female representation in European parliaments

A map showing the proportion of women in each national parliament (specifically the lower house in countries with bicameral legislature). Source: https://data.ipu.org/women-ranking/?date_year=2024&date_month=11 (supplemented by a Google search for the non full UN members — Vatican City, Palestine, Kosovo — and dependent territories — Jersey, Guernsey, Faroe Islands, Gibraltar).

The highest proportion in Europe is Andorra, where precisely half of the 28 elected members of the General Council are women. The lowest meanwhile is Vatican City, where just one out of the 8 appointed members of the Pontifical Commission is a woman. The lowest among elected chambers is Cyprus, where 8 out of the 56 members of the House of Representatives are women.

Worldwide, four (lower) chambers currently have over 50% women: Rwanda's Chamber of Deputies (64%), Cuba's National Assembly of People's Power (56%), Nicaragua's National Assembly (54%) and Mexico's Chamber of Deputies (50.2%). Alongside Andorra, two more have precisely half: Namibia's National Assembly and the United Arab Emirates Federal National Council (the latter due to a quota). The US House of Representatives is at 29%, China's National People's Congress at 27%, Brazil's Chamber of Deputies at 18% and India's Lok Sabha at 14%.
"""

# generate map
df = pd.read_csv("datasets/women-ranking--2024-11--export--241207-171225--EN.csv", skiprows=15, index_col=1)
df = (100 * df["Women"].apply(lambda s: 0 if s == "-" else float(s)) / df["Seats"].apply(lambda s: 0 if s == "-" else float(s)))
df.rename(index={
    'Bosnia and Herzegovina':'Bosnia',
    "Türkiye": "Turkey",
    "United Kingdom": "UK",
    "Czechia": "Czech Republic",
    "Russian Federation": "Russia",
    "Republic of Moldova": "Moldova",
    "North Macedonia": "Macedonia",
    "Iran (Islamic Republic of)": "Iran",
    "Syrian Arab Republic": "Syria",
},inplace=True)

def pc(x, y): return x / y * 100

df["Kosovo"] = pc(40, 120)
df["Palestine"] = 19
df["Jersey"] = pc(20, 54)
df["Guernsey"] = pc(8, 40)
df["Faroe Islands"] = pc(10, 33)
df["Gibraltar"] = pc(4, 17)
df["Vatican City"] = pc(1, 8)

# Palestine, Kosovo

FONT = sans
CUTOFFS = [45, 40, 35, 30, 25, 20, 0, 0]
LABELS = [ f"under {i}%" if j == 0 else f"{j}% to 50%" if i == 0 else f"{j}% to {i}%" for i,j in generate_ngrams([0] + CUTOFFS[:-1], 2) ]
PALETTE = """#fff7fb
#ece2f0
#d0d1e6
#a6bddb
#67a9cf
#3690c0
#02818a
#016c59
#014636""".split()[::-1][:-2]



def colorfn(c):
    if c in ['Sea', 'Borders']:
        return "white"
    elif c not in df.index:
        return print(c) or "grey"
    return PALETTE[next(i for i, x in enumerate(CUTOFFS) if df[c] >= x)]


def labelfn(c, w, h):
    if c not in df.index: return None
    if c in ["Monaco", "Vatican City", "Faroe Islands"]: return None
    label = f"{floor(df[c] + 0.5)}%"
    return Image.from_text(label, FONT(20), "black" if df[c] < 40 else "white")

map = map_chart("maps/Europe2.png", colorfn, labelfn)

HEADER = "Female MPs"
legend = generate_legend(PALETTE, LABELS, box_sizes=40,
                         header=HEADER, font_family=partial(FONT, 24))
chart = map.place(legend, align=(1, 0), padding=(40,60))

title = Image.from_column([
    Image.from_text("proportion of female parliamentarians".upper(), FONT(48, bold=True)),
    Image.from_markup("Female MPs in the lower/single house. Sourced from [[https:\//data.ipu.org/women-ranking/]], Nov 2024.", partial(FONT, 24))],
    padding=4,
    bg="white")

img = Image.from_column([title, chart], bg="white", padding=2)
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black",padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/eufemalemps.png")
