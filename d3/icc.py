from pudzu.pillar import *
from generate import *

nons = """Azerbaijan
Belarus
Bhutan
Brunei
China
Cuba
Equatorial Guinea
Ethiopia
India
Indonesia
Iraq
Kazakhstan
North Korea
Laos
Lebanon
Libya
Malaysia
Mauritania
Myanmar
Nepal
Nicaragua
Niue
Pakistan
Palau
Papua New Guinea
Qatar
Rwanda
Saudi Arabia
Singapore
Somalia
South Sudan
Sri Lanka
Swaziland
Togo
Tonga
Turkey
Turkmenistan
Tuvalu
Vatican City
Vietnam
Israel
Russia
United States""".split("\n")

signed = """Algeria
Angola
Bahamas
Bahrain
Cameroon
Egypt
Eritrea
Guinea-Bissau
Haiti
Iran
Jamaica
Kuwait
Kyrgyzstan
Monaco
Morocco
Mozambique
Oman
São Tomé and Príncipe
Solomon Islands
Syria
Thailand
United Arab Emirates
Uzbekistan
Yemen
Zimbabwe""".split("\n")

indicted = [
    "Democratic Republic of the Congo", "Uganda", "Central African Republic", "Sudan", "Kenya", "Libya", "Ivory Coast",
    "Mali", "Georgia", "Palestine", "Ukraine"
        ]
ongoing = ["Bangladesh", "Burundi", "Afghanistan", "Philippines", "Venezuela"]
preliminary = ["Nigeria", "Lithuania"]
closed = ["Colombia", "Iraq", "Honduras", "South Korea", "Comoros", "Gabon", "Bolivia"]
# TODO: former
countries = nons + indicted + ongoing  + preliminary + closed + signed


# Sudan and Myanmar reffered by
# Burundi and Philippines have withdrawn
# Bangladesh is for
assert set(countries) < set(load_name_csv("../dataviz/maps/World.png").name), f'Unrecognised countries: {set(countries) - set(load_name_csv("../dataviz/maps/World.png").name)}'

def colorfn(c):
    if c in ['Sea', 'Borders']: return "white"
    elif c in indicted: return VegaPalette10.RED
    elif c in ongoing: return VegaPalette10.ORANGE
    elif c in preliminary: return VegaPalette10.PINK
#    elif c in closed: return VegaPalette10.GREEN
    elif c in nons: return "#909090"
    elif c in signed: return "#909090"
    else: return "#C0C0C0"

colormap = { c: colorfn(c) for c in countries }
colormap["somaliland"] = colorfn("Somalia")
colormap["TWN"] = colormap["ESH"] = colorfn("Somalia")

atlas = pd.read_csv("../dataviz/datasets/countries.csv").split_columns('country', "|").explode('country').set_index('country')
CODES = pd.Series(atlas.code.index.values, index=atlas.code )
labels = { "DR Congo": 6, "Uganda": 5, "Sudan": 7, "Central African Republic": 5 + 6, "Kenya": 9,
           "Libya": 11, "Cote D'Ivoire": 3, "Mali": 3, "Georgia": 3, "Palestinian Territories": 3, "Ukraine": 6}
LABELS = { code: labels.get(country, " ") for code, country in CODES.items() }
for C in ["BES", "BVT", "UMI", "HMD", "northern_cyprus", "somaliland", "kosovo"]: LABELS[C] = " "


generate_datamap("icc", colormap, labels=LABELS, label_size=16, default_fill=colorfn("shlabada"))

chart = Image.open("temp/icc.png")
legend = generate_legend(
  [VegaPalette10.RED,VegaPalette10.ORANGE,VegaPalette10.PINK,colorfn("Israel"),colorfn("shlabada")
   ],
  ["ICC investigation leading to indictments (with # of indictments)",
   "Ongoing ICC investigation with no indictments as yet",
   "Ongoing ICC preliminary examination",
   "Non-parties to the Rome Statute (including signatory states that have yet to ratify it)",
   "Parties to the Rome Statute",
#  "Acting colonial governor"
], 40, partial(arial, 16),
    max_width=500,
    footer="""Non-parties to the Rome Statute are normally safe from investigation. However: (1) Sudan and Libya were referred by the UN Security Council (though a resolution to refer Syria was vetoed by Russia and China); (2) Myanmar, Russia and Israel are being investigated for actions committed in states that either were party to the Statute or accepted ad hoc ICC jurisdiction; and (3) Burundi and the Philippines withdrew from the Statute only after their investigations were opened.""")
chart = chart.place(legend, align=(0,1), padding=100)

title = Image.from_column([
Image.from_text("ICC INVESTIGATIONS AND INDICTMENTS AS OF 2024", sans(72, bold=True)),
Image.from_text("investigations and indictments issued by the International Criminal Court pursuant to the Rome Statute", sans(36, italics=True))
], bg="white")

footer = Image.from_markup("mostly sourced from [[https:\//en.wikipedia.org/wiki/List_of_Jewish_heads_of_state_and_government]]", partial(sans, 32))

img = Image.from_column([title, chart], bg="white", padding=5)
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/icc.png")
