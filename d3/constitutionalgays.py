from pudzu.charts import *
from generate import *

FONT = sans

PALETTE = {
"j": "#a6cee3",
"f": "#b2df8a",
 }
DESCRIPTIONS = {
"j": "in the Constitution",
"f": "in a quasi-constitutional Act"
}

CONSTITUTION = {
"Bolivia": 2009,
"Cuba": 2019,
"Ecuador": 1998,
"Fiji": 1997,
"Kosovo": 2008,
"Malta": 2014,
"Mexico": 2011,
"Portugal": 2004,
"South Africa": 1996,
"Sweden": 2011,
}
ACT = {
    "New Zealand": 1993,
    "Canada": 2016,

}
LABELS = { k: str(v) for k,v in (CONSTITUTION | ACT).items() }
CODES = pd.Series(atlas.code.index.values, index=atlas.code )
L = { code: LABELS.get(country, " ") for code, country in CODES.items() }
for C in ["BES", "BVT", "UMI", "HMD", "northern_cyprus", "somaliland"]: L[C] = " "
L["kosovo"] = LABELS["Kosovo"]

colormap = {}
for x in CONSTITUTION: colormap[x] = "j"
for x in ACT: colormap[x] = "f"

generate_datamap("constitutionalgays", colormap, palette=PALETTE, codifier=partial(codify_countries, dependencies=True), labels=L)

chart = Image.open("temp/constitutionalgays.png")
legend = generate_legend(
  [PALETTE[c] for c in DESCRIPTIONS],
  [DESCRIPTIONS.get(c,c) for c in DESCRIPTIONS],
  (40,...), partial(sans, 16), header="Discrimination banned".upper())
chart = chart.place(legend, align=(0,1), padding=100)

title = Image.from_column([
Image.from_text("CONSTITUTIONAL PROTECTION OF GAY RIGHTS", sans(72, bold=True)),
Image.from_text("countries whose constitutions explicitly ban discrimination on the basis of sexual orientation ", sans(36, italics=True))
], bg="white")

img = Image.from_column([title, chart], bg="white", padding=5)
img.place(Image.from_text("/u/Udzu", sans(16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/constitutionalgays.png")

