from pudzu.pillar import *
from generate import *

countries = [
    "Peru", "Iceland", "Israel", "Germany", "United Kingdom", "Croatia",
    "Albania", "Armenia", "France", "Turkmenistan", "Poland", "Costa Rica",
    "Guyana", "Cyprus", "Hungary", "Ivory Coast", "Kazakhstan"
]

assert set(countries) < set(load_name_csv("../dataviz/maps/World.png").name), f'Unrecognised countris: {set(countries) - set(load_name_csv("../dataviz/maps/World.png").name)}'

def colorfn(c):
    if c in ['Sea', 'Borders']: return "white"
    if c in countries: return PairedClass12.BLUE
    else: return "grey"

colormap = { c: colorfn(c) for c in countries }
colormap["somaliland"] = "#BBBBBB"
generate_datamap("jewishfirstladies", colormap)

chart = Image.open("temp/jewishfirstladies.png")
# legend = generate_legend(
#   [PairedClass12.BLUE,PairedClass12.LIGHTBLUE,PairedClass12.GREEN,
#    #PairedClass12.LIGHTGREEN
#    ],
#   ["Head of government (president, PM, etc)",
#    "(unconfirmed Jewish heritage)",
#   "Colonial or national governor",
# #  "Acting colonial governor"
# ], 40, partial(arial, 16), header="JEWISH OR HALF-JEWISH")
# chart = chart.place(legend, align=(0,1), padding=100)

title = Image.from_column([
Image.from_text("COUNTRIES THAT HAVE HAD A JEWISH FIRST LADY", sans(72, bold=True)),
], bg="white")

img = Image.from_column([title, chart], bg="white", padding=5)
#img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/politics_jewishfirstladies.png")
