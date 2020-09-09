from pudzu.charts import *
from generate import *

# t: from te
# ot: + other morpheme: dute, herbata
# c: from cha
# oc: + other morpheme

FONT = sans
DEFAULT = VegaPalette10.GREEN
PALETTE = {"current": VegaPalette10.ORANGE, "old": VegaPalette10.BLUE, "other": VegaPalette10.LIGHTBLUE}

NAMES = ["pound", "franc", "dollar"]

pound = { "current":  {"UK", "Egypt", "Falkland Islands", "Gibraltar", "Guernsey", "Isle of Man", "Jersey", "Lebanon", "Saint Helena", "South Sudan", "Sudan", "Syria"},
"old": { "Botswana", "Lesotho", "Swaziland", "Australia", "New Zealand", "Ireland", "Bahamas", "Bermuda", "Nigeria", "Cyprus", "Fiji", "Namibia", "Ghana", "Israel", "Jamaica", "Libya", "Jordan", "Palestine", "Canada", "Malawi", "Malta", "Papua New Guinea", "Zimbabwe", "Malawi", "Zambia", "Samoa", "South Africa", "Tonga", "Cayman Islands", "Turks and Caicos Islands", "Gambia", "Liberia", "Sierra Leone", "Namibia" },
"other": { "Kenya", "Tanzania", "Uganda", "USA" } }

franc = { "current": {"Benin", "Burkina Faso", "Burundi", "Cameroon", "Central African Republic", "Chad", "Congo", "DR Congo", "Comoros", "Ivory Coast", "Djibouti", "Equatorial Guinea", "Gabon", "Guinea", "Guinea-Bissau", "Liechtenstein", "Mali", "Niger", "Rwanda", "Senegal", "Switzerland", "Togo", "New Caledonia", "Wallis and Futuna", "French Polynesia" },
"old": { "France", "French Guiana", "Guadeloupe", "Martinique", "Algeria", "Andorra", "Belgium", "Luxembourg", "Madagascar", "Mauritania", "Monaco", "Morocco", "Tunisia"} }

dollar = { "current": { "USA", "Panama", "Puerto Rico", "Guam", "American Samoa", "Namibia", "Canada", "Australia", "New Zealand", "Antigua and Barbuda", "Anguilla", "Dominica", "Grenada", "Montserrat", "Saint Kitts and Nevis", "Saint Lucia", "Saint Vincent and the Grenadines", "Bahamas", "Barbados", "Belize", "Bermuda", "Belize", "Brunei", "Singapore", "Cayman Islands", "East Timor", "El Salvador", "Ecuador", "Fiji", "Guyana", "Hong Kong", "Jamaica", "Kiribati", "Liberia", "Marshall Islands", "Micronesia", "Nauru", "Palau", "Suriname", "Taiwan", "Hong Kong", "Trinidad and Tobago", "Tuvalu", "Zimbabwe" } ,
"old": { "Ethiopia", "Malaysia", "Sierra Leone", "Sierra Leone", "Spain" } }

DATA = [pound, franc, dollar]

DESCRIPTIONS = { "current": "Currently in use", "old": "Used historically", "other": "The British colonies in America used pounds before independence. East Africa used a shilling-based system that included a pound (=20s)." }

for data in DATA:
    for values in data.values():
        assert values < set(atlas.index), f'Unrecognised countries: {set(values) - set(atlas.index)}'

for name,data in zip(NAMES, DATA):
    colormap = { c: PALETTE[i] for i,cs in data.items() for c in cs }
    generate_datamap(name, colormap, palette=PALETTE, codifier=partial(codify_countries, dependencies=False))


charts = []
for name, data in zip(NAMES, DATA):
    chart = Image.open(f"temp/{name}.png").trim((0,0,0,20))
    legend = generate_legend(
      [PALETTE[c] for c in data.keys()],
      [DESCRIPTIONS[c] for c in data.keys()],
      (40,...), partial(sans, 24), header=Image.from_text(f"{name}".upper(), FONT(48, bold=True), padding=(0,5)), max_width=400)
    chart = chart.place(legend, align=(0,1), padding=100)
    charts.append(chart)

title = Image.from_column([
Image.from_text("POUNDS, FRANCS AND DOLLARS", sans(96, bold=True)),
Image.from_text("currencies with those names, today and historically", sans(56, italics=True), padding=(0,0,0,20))],
bg="white")

img = Image.from_column([title, *charts], bg="white", padding=5)
img.place(Image.from_text("/u/Udzu", sans(16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/currencies.png")

