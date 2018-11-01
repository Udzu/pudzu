from pudzu.charts import *

# https://www.webcitation.org/5msUtFmJu?url=http://aa.usno.navy.mil/faq/docs/minorplanets.php

FONT = calibri
SIZE = 20

df = pd.read_csv("datasets/planets.csv").split_columns("planets", "|").assign_rows(n=lambda d: len(d['planets'])).fillna("")

SYMBOLS = {
"Moon": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c6/Moon_symbol_decrescent.svg/500px-Moon_symbol_decrescent.svg.png",
"Sun": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Sun_symbol.svg/600px-Sun_symbol.svg.png",
"Mercury": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2e/Mercury_symbol.svg/600px-Mercury_symbol.svg.png",
"Venus": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/66/Venus_symbol.svg/600px-Venus_symbol.svg.png",
"Earth": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Earth_symbol.svg/600px-Earth_symbol.svg.png",
"Mars": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b7/Mars_symbol.svg/600px-Mars_symbol.svg.png",
"Jupiter": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/26/Jupiter_symbol.svg/600px-Jupiter_symbol.svg.png",
"Saturn": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/74/Saturn_symbol.svg/600px-Saturn_symbol.svg.png",
"Uranus": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f1/Uranus_symbol.svg/600px-Uranus_symbol.svg.png",
"Neptune": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/Neptune_symbol.svg/600px-Neptune_symbol.svg.png",
"Pluto": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/ff/Pluto_symbol.svg/600px-Pluto_symbol.svg.png",
"Eris": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8b/Five_fingered_hand_of_Eris_symbol.svg/600px-Five_fingered_hand_of_Eris_symbol.svg.png",
"Ceres": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/37/Ceres2.svg/303px-Ceres2.svg.png",
"Pallas": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/57/2Pallas_symbol.svg/394px-2Pallas_symbol.svg.png",
"Juno": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ed/3_Juno_%281%29.svg/337px-3_Juno_%281%29.svg.png",
"Vesta": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/20/4_Vesta_%281%29.svg/429px-4_Vesta_%281%29.svg.png",
"Astraea": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bf/5_Astraea_Symbol.svg/473px-5_Astraea_Symbol.svg.png",
"Hebe": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b2/6_Hebe_Astronomical_Symbol.svg/464px-6_Hebe_Astronomical_Symbol.svg.png",
"Iris": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/7_Iris_Astronomical_Symbol.svg/800px-7_Iris_Astronomical_Symbol.svg.png",
"Flora": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5a/8_Flora_Astronomical_Symbol.svg/591px-8_Flora_Astronomical_Symbol.svg.png",
"Metis": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dc/9_Metis_symbol.svg/741px-9_Metis_symbol.svg.png",
"Hygiea": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/10_Hygiea_Astronomical_Symbol.svg/273px-10_Hygiea_Astronomical_Symbol.svg.png",
"Parthenope": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0c/11_Parthenope_symbol.svg/285px-11_Parthenope_symbol.svg.png",
"Victoria": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2b/Victoria_asteroid_symbol.svg/512px-Victoria_asteroid_symbol.svg.png",
"Egeria": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/72/13_Egeria_symbol.svg/480px-13_Egeria_symbol.svg.png"
}

# TODO: colors, asteroid symbols

CATEGORIES = OrderedDict([
("Star", (VegaPalette10.ORANGE, "Sun")),
("Terrestrial planet", (VegaPalette10.BLUE, { "Mercury", "Venus", "Earth", "Mars"})),
("Giant planet", (VegaPalette10.RED, {"Jupiter", "Saturn", "Uranus", "Neptune"})),
("Satellite", ("#909090", "Moon|Ganymede|Callisto|Io|Europa|Titan|Iapetus|Rhea|Tethys|Dione".split("|"))),
("Asteroid", (VegaPalette10.BROWN, "Vesta|Juno|Ceres|Pallas|Astraea|Hebe|Iris|Flora|Metis|Hygiea|Parthenope|Victoria|Egeria".split("|"))),
("Trans-Neptunian object", (VegaPalette10.PURPLE, "Pluto|Eris")),
])

def symbol(n):
    col = next(c for c,v in CATEGORIES.values() if n in v)
    img = Image.from_url_with_cache(SYMBOLS.get(n, "https://upload.wikimedia.org/wikipedia/commons/thumb/5/57/Full_moon_symbol.svg/600px-Full_moon_symbol.svg.png")).to_rgba().pad_to_aspect(1, bg=None)
    return img.remove_transparency(col).resize((SIZE, SIZE))

def colorfn(c,r):
    def pattern(size):
        if (size[0] == 0): return Image.EMPTY_IMAGE
        return Image.from_row([symbol(p) for p in df.planets[df.index[r]]])
    return pattern

chart = bar_chart(df[['n']], SIZE, SIZE*df.n.max(), spacing=2, horizontal=True, label_font=FONT(14), 
                  grid_interval=1, label_interval=5, ymax=21, colors=colorfn,
                  clabels={ BarChartLabelPosition.OUTSIDE: lambda c,r: Image.from_text(df.description[df.index[r]] and " ({})".format(df.description[df.index[r]]), FONT(14), "black", "white", beard_line=True, padding=2) },
                  rlabels = {BarChartLabelPosition.BELOW: lambda r: df.date[df.index[r]] },
                  ylabel=Image.from_text("number of recognised planets", FONT(16), padding=(5,2,5,10)))
      
COMMENT = """• **The seven classical planets** were known to the Babylonians, and were named  πλανῆται planētai ("//wanderers//") by the Greeks since they moved across the sky relative to the fixed stars. These are also the source of the names of the seven days of the week: Saturday (Saturn), Sunday (Sun) and Monday (Moon) are still obvious in English, while Mardi (Mars), Mercredi (Mercury), Jeudi (Jupiter), Vendredi (Venus) are clearer in French.
• **The satellites orbiting Jupiter and Saturn** were initially described as planets too, even by Copernicans such as Galileo ("//I should disclose and publish to the world the occasion of discovering and observing four Planets, never seen from the beginning of the world up to our own times//"). Furthermore, the Copernican model was not widely accepted until the 1700s–not for theological reasons, but because at the time it was still scientifically unsound (its problems with stellar parallax, rotation inertia and circular orbits had not yet been solved). 
• **The early asteroids** were also considered planets, and assigned planetary symbols. Following the rush of discoveries starting in 1847, symbolic notation was dropped for the minor asteroids, but only after over a dozen had already been assigned. The four big asteroids (Ceres, Pallas, Juno and Vesta) continued to be listed as planets until the 1860s.
• **Pluto** was widely considered a planet, and **Eris** was breifly described as a tenth planet by NASA following its discovery. However, **Chiron** was only described as a planet by the media and astrologers, and **Charon** was never officially considered part of a double planet with Pluto."""

comment = Image.from_markup(COMMENT, partial(FONT, 12), max_width=250, bg="white")
legend = generate_legend([c for c,_ in CATEGORIES.values()], [l for l in CATEGORIES], fonts=partial(FONT, 16), box_sizes=20, header="Classification", footer=comment)

img = Image.from_row([chart, legend], yalign=1, padding=5)
title = Image.from_text("Historically recognised planets".upper(), FONT(40, bold=True))

img = Image.from_column([title, img], bg="white", padding=8)
img = Image.from_column([img, Image.from_text("/u/Udzu", font("arial", 12), fg="grey", bg="white", padding=5).pad((1,1,0,0), "grey")], bg="white", xalign=1)
img.save("output/planets.png")
