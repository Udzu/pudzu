from pudzu.charts import *
from pudzu.pillar import *


QUALIFY = ["Scotland", "Albania", "Bosnia", "Latvia", "Finland", "Macedonia"]
NON_QUALIFY = [
    "Lithuania", "Estonia", "Moldova", "Cyprus", "Malta", "Luxembourg", "Andorra", "Armenia",
    "Azerbaijan", "Belarus", "Faroe Islands", "San Marino", "Gibraltar", "Kazakhstan",
    "Kosovo", "Liechtenstein", "Montenegro",
]
NON_EUROPE = ["Iran", "Iraq", "Saudi Arabia", "Palestine", "Jordan", "Syria", "Vatican City",
              "Lebanon", "Algeria", "Tunisia", "Morocco"]

FONT = sans

def colorfn(c):
    if c in ["Sea", "Borders"]: return "white"
    elif c in NON_EUROPE: return "#D0D0D0"
    elif c in ["Israel"]: return Stripe(20, VegaPalette10.BLUE, VegaPalette10.GREEN)
    elif c in QUALIFY: return VegaPalette10.BLUE
    elif c in NON_QUALIFY: return VegaPalette10.GREEN
    return "#A0A0A0"


map2 = map_chart("maps/Europe2.png", colorfn)
mapuk = map_chart("maps/EuropeUK.png", colorfn)
map = map2.overlay(mapuk.crop((100,300,400,800)), (100,300), copy=True)

legend = generate_legend(
    [
        Rectangle(40, VegaPalette10.GREEN).place(Image.from_text(str(len(NON_QUALIFY)), FONT(16, bold=True), "white")),
        Rectangle(40, Stripe(20, VegaPalette10.BLUE, VegaPalette10.GREEN)).place(Image.from_text("1", FONT(16, bold=True), "white")),
        Rectangle(40, VegaPalette10.BLUE).place(Image.from_text(str(len(QUALIFY)), FONT(16, bold=True), "white")),
        Rectangle(40, "#A0A0A0").place(Image.from_text(str(55-len(QUALIFY)-len(NON_QUALIFY)-1), FONT(16, bold=True), "white"))
    ],
    [
        "not qualified",
        "not qualified in UEFA",
        "group stages",
        "knockout stages"
    ],
    font_family = partial(FONT, 24),
    header="BEST PERFORMANCE")
map = map.place(legend, align=(1,0), padding=50)

# TODO: legend

title = Image.from_column([
Image.from_text("UEFA'S FOOTBALLING MINNOWS", FONT(72, bold=True)),
Image.from_text('countries yet to progress past the group stages at either the Euros or World Cup', FONT(36))],
bg="white", padding=2)

img = Image.from_column([title, map], bg="white", padding=2)
img.place(Image.from_text("/u/Udzu", font("arial", 18), fg="black", bg="#FFFFFF80", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/eufootballminnows.png")
