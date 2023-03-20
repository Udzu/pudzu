from pudzu.charts import *
from pudzu.sandbox.bamboo import *
import seaborn as sns

df = pd.read_csv("datasets/euusancestry.csv").set_index("country")
atlas = pd.read_csv("datasets/countries.csv").split_columns('country', "|").explode('country').set_index('country').population
atlas["England"] = 56315000
atlas["Scotland"] = 5471000
atlas["Wales"] = 3146000
atlas["Northern Ireland"] = 1904000

MIX = { "Czechoslovakia": ["Slovakia", "Czech Republic"],
        "Yugoslavia": ["Bosnia", "Macedonia", "Montenegro", "Serbia", "Slovenia", "Croatia"],
        "UK": ["England", "Scotland", "Wales", "Northern Ireland"]
    }#
ASTERISK = {x for cs in MIX.values() for x in cs} | { "Ireland" }
FONT = sans

for a,cs in MIX.items():
    total_pop = sum(atlas[c] for c in cs)
    for c in cs:
        if c in df.index:
            df.ancestry[c] += int(round(df.ancestry[a] * (atlas[c] / total_pop)))

atlas["Ireland"] += atlas["Northern Ireland"]
df.ancestry["Ireland"] += df.ancestry["Northern Ireland"]

df["pc"] = (df["ancestry"] / atlas) * 100

CUTOFFS = [100, 50, 20, 10, 5, 2, 1, 0]
PALETTE = [VegaPalette10.RED] + """#f1eef6
#d0d1e6
#a6bddb
#74a9cf
#3690c0
#0570b0
#034e7b""".split("\n")[::-1]

def colorfn(c):
    if c in ["Sea", "Borders"]: return "white"
    elif c not in df.index: return "#A0A0A0"
    return PALETTE[next(i for i, x in enumerate(CUTOFFS) if df.pc[c] >= x)]

def maybe_int(x):
    return int(x) if x == int(x) else x

def labelfn(c):
    if c == "Spain":
        return Image.from_text("*", FONT(2))
    if c in df.index:
        label = "{}%".format(maybe_int(round_significant(df.pc[c], 2)))# + ("*" * (c in ASTERISK))
        color = "white" if 50 <= df.pc[c] <= 100 else "black"
        return Image.from_text(label, FONT(20), color)

map2 = map_chart("maps/Europe2.png", colorfn, labelfn)
mapuk = map_chart("maps/EuropeUK.png", colorfn)

map = map2.overlay(mapuk.crop((100,300,400,800)), (100,300), copy=True)
map.overlay(labelfn("Ireland"), (185,600))
map.overlay(labelfn("Wales"), (250,650))
map.overlay(labelfn("England"), (315,660))
map.overlay(labelfn("Scotland"), (280,500))


"* "
"Scotch-Irish counted as Northern Ireland, Irish as Ireland and Albanian as Albania."

HEADER = "Diaspora as % of country"
FOOTER = "////**EU total: 1,078,700 (0.21%)\nEurope total: 1,359,100 (0.17%)\nWorld total: 14,511,100 (0.20%)**"
LABELS = [ f"over {j:,}%" if i == 0 else f"less than {i:,}%" if j == 0 else f"{j:,}% to {i:,}%" for i,j in generate_ngrams([0] + CUTOFFS, 2) ]
legend = generate_legend(PALETTE + ["#A0A0A0"],  LABELS + ["not listed"], box_sizes=40, header=HEADER, font_family=partial(FONT, 24))
chart = map.place(legend, align=(1,0), padding=20)

title = Image.from_column([
Image.from_text("US DIASPORAS AS % OF COUNTRY OF ORIGIN'S POPULATION", FONT(48, bold=True)),
Image.from_text('based on self-reported "ancestry or ethnic origin" in the American Community Survey, 2021', FONT(36))],
bg="white", padding=2)
footer = Image.from_markup('Source: [[https:\//data.census.gov/table?t=Ancestry&d=ACS+5-Year+Estimates+Detailed+Tables&tid=ACSDT5Y2021.B04006]].\n'
'//British//, //Czechoslovakian// and //Yugoslavian// ancestries were split among their constituent countries according to current populations.\n'
"//Irish// and //Scotch-Irish// ancestries were counted against the whole island of Ireland (both Ireland and Northern Ireland).\n"
"//Croatian//, //Serbian// and //Albanian// ancestries were counted just against those countries, though probably apply more widely.\n"
"//Spanish// ancestry is not listed, perhaps due to its intersection with //Hispanic// identity. According to Wikipedia, the number would be ~3%."
, partial(arial, 24), "black", "white", max_width=chart.width-120, padding=(0,5,20,5))

img = Image.from_column([title, chart, footer], bg="white", padding=2)
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/euusancestry.png")
