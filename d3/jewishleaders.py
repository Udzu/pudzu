from pudzu.pillar import *
from generate import *

leader = [
    "Latvia", "Ethiopia",
  "El Salvador", "Honduras", "United Kingdom", "New Zealand", "Italy",
   "Russia", "Panama", "Guyana",
  "Switzerland", "France", "Peru", "Ukraine",
   "Hungary", "Austria", "Democratic Republic of the Congo",
   "Romania", "Bulgaria", "Georgia", "Czech Republic", "Belgium", "Israel", "Armenia", "Mexico", "Dominican Republic"
]
unconfirmed = ["Venezuela", "Tunisia"]
premodern = ["Yemen", "Iran", "Egypt"]
governors = [
  "United States Virgin Islands", "Ghana", "Hong Kong", "Rwanda", "Madagascar",
  "Republic of the Congo", "Palestine", "Jordan", "India", "Pakistan", "Bangladesh",
  "Kazakhstan", "Turkmenistan", "Uzbekistan", "Australia", "Somalia", "Tajikistan",
  "Martinique", "Kyrgyzstan", "Mali", "Togo", "Uganda", "Singapore", "Zimbabwe", "Zambia", "Malawi", "Gibraltar"
  ]
acting_governors = [
  "Sierra Leone", "Central African Republic", "Chad", "Gabon", 
  "Benin", "Burkina Faso", "Ivory Coast", "Guinea", "Mauritania", "Niger"
]
countries = leader + premodern + governors  + unconfirmed # + acting_governors

assert set(countries) < set(load_name_csv("../dataviz/maps/World.png").name), f'Unrecognised countris: {set(countries) - set(load_name_csv("../dataviz/maps/World.png").name)}'

def colorfn(c):
    if c in ['Sea', 'Borders']: return "white"
    if c in leader: return PairedClass12.BLUE
    elif c in unconfirmed: return PairedClass12.LIGHTBLUE
    elif c in premodern: return PairedClass12.BLUE
    elif c in governors: return PairedClass12.GREEN
    elif c in acting_governors: return PairedClass12.LIGHTGREEN
    else: return "grey"

colormap = { c: colorfn(c) for c in countries }
colormap["somaliland"] = "#BBBBBB"
generate_datamap("jewishleaders", colormap)

chart = Image.open("temp/jewishleaders.png")
legend = generate_legend(
  [PairedClass12.BLUE,PairedClass12.LIGHTBLUE,PairedClass12.GREEN,
   #PairedClass12.LIGHTGREEN
   ],
  ["Head of government (president, PM, etc)",
   "(unconfirmed Jewish heritage)",
  "Colonial or national governor",
#  "Acting colonial governor"
], 40, partial(arial, 16), header="JEWISH OR HALF-JEWISH")
chart = chart.place(legend, align=(0,1), padding=100)

title = Image.from_column([
Image.from_text("JEWISH HEADS OF GOVERNMENT", sans(72, bold=True)),
Image.from_text("countries that have had a head of government of full or half Jewish heritage", sans(36, italics=True))
], bg="white")

footer = Image.from_markup("mostly sourced from [[https:\//en.wikipedia.org/wiki/List_of_Jewish_heads_of_state_and_government]]", partial(sans, 32))

img = Image.from_column([title, chart, footer], bg="white", padding=5)
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/politics_jewishleaders.png")
