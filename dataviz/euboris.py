from pudzu.charts import *
from pudzu.sandbox.bamboo import *
import seaborn as sns


flags = pd.read_csv("../dataviz/datasets/countries.csv").split_columns(('country'), "|").explode('country').set_index('country').flag

countries = {"UK": "Johnson", "Serbia": "Tadić", "Macedonia": "Trajkovski", "Russia": "Yeltsin",
             "Bulgaria": "III", "Andorra": "Skossyreff", "Slovenia": "Kidrič", "Ukraine": "Martos"}
images = {
    "UK": "https://ichef.bbci.co.uk/news/976/cpsprodpb/28BE/production/_107503401_2209c8a2-6bff-4e22-ba6b-e3e2ed9eaede.jpg",
    "Bulgaria": "https://upload.wikimedia.org/wikipedia/commons/6/6a/Boris_III_of_Bulgaria.jpg",
    "Slovenia": "https://upload.wikimedia.org/wikipedia/commons/a/a0/Boris_Kidri%C4%8D_%281%29.jpg",
    "Andorra": "https://histoiresroyales.fr/wp-content/uploads/2020/02/roi-andorre-boris-skossyreff-histoire-1200x900.jpg",
    "Serbia": "https://upload.wikimedia.org/wikipedia/commons/9/9d/Boris_Tadic_2010.jpg",
    "Macedonia": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/73/%D0%91%D0%BE%D1%80%D0%B8%D1%81_%D0%A2%D1%80%D0%B0%D0%B9%D0%BA%D0%BE%D0%B2%D1%81%D0%BA%D0%B8%D0%B9_%2807-03-2002%29_%28cropped%29.jpg/220px-%D0%91%D0%BE%D1%80%D0%B8%D1%81_%D0%A2%D1%80%D0%B0%D0%B9%D0%BA%D0%BE%D0%B2%D1%81%D0%BA%D0%B8%D0%B9_%2807-03-2002%29_%28cropped%29.jpg",
    "Russia": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/45/%D0%91%D0%BE%D1%80%D0%B8%D1%81_%D0%9D%D0%B8%D0%BA%D0%BE%D0%BB%D0%B0%D0%B5%D0%B2%D0%B8%D1%87_%D0%95%D0%BB%D1%8C%D1%86%D0%B8%D0%BD-1_%28cropped%29_%28cropped%29.jpg/220px-%D0%91%D0%BE%D1%80%D0%B8%D1%81_%D0%9D%D0%B8%D0%BA%D0%BE%D0%BB%D0%B0%D0%B5%D0%B2%D0%B8%D1%87_%D0%95%D0%BB%D1%8C%D1%86%D0%B8%D0%BD-1_%28cropped%29_%28cropped%29.jpg",
    "Ukraine": "https://upload.wikimedia.org/wikipedia/commons/0/02/Martos_Borys.jpg"
}

dates = { "UK": "Prime Minister, 2019–22(?)", "Serbia": "President, 2004–12", "Russia": "President, 1991–99",
          "Macedonia": "President, 1999–04", "Slovenia": "Prime Minister, 1945–46",
          "Bulgaria": "Tsar, 1918–43", "Andorra": "King, July 1934",
          "Ukraine": "Council Chair, 1919"}

def colorfn(c):
    if c not in countries:
        return "white" if c in ['Sea', 'Borders'] else "#AAAAAA"
    else:
        return VegaPalette10.BLUE

@ignoring_exceptions
def labelfn(c, w, h):
    return Image.from_text(countries[c], arial(20, bold=True))


map = map_chart("maps/Europe2.png", colorfn, labelfn)
map = map.pin(Image.from_text(countries["Andorra"], arial(20, bold=True)), (340, 970))
map = map.pin(Image.from_text(countries["Macedonia"], arial(20, bold=True)), (860, 1015))

chart = map # map.place(legend, align=(1,0), padding=10)

DEFAULT_IMG = "https://s-media-cache-ak0.pinimg.com/736x/0d/36/e7/0d36e7a476b06333d9fe9960572b66b9.jpg"

portraits = Image.from_row([Image.from_column([
    Image.from_url_with_cache(images.get(c, DEFAULT_IMG)).to_rgba().crop_to_aspect(100, 100, (0.5, 0 if c in ("Andorra", "Bulgaria", "Ukraine") else 0.2)).resize_fixed_aspect(width=185),
    Image.from_row([
        Image.from_url_with_cache(flags[c]).to_rgba().resize_fixed_aspect(height=15).pad(1, "grey"),
        Image.from_text(n.upper(), arial(20, bold=True), beard_line=True),
        ], padding=(3,0)),
    Image.from_text(dates.get(c, "??"), arial(16)),
]) for c,n in sorted(countries.items(), key=lambda kv: kv[1])], padding=5).pad((0,0,0,5), "white")

# title
title = Image.from_column([
Image.from_text("A quorum of Borises".upper(), arial(96, bold=True)),
Image.from_text("countries which have had a head of state or head of government called Boris", arial(36, italics=True)),
],
bg="white")

img = Image.from_column([title, chart, portraits], bg="white", padding=2)
#img.place(Image.from_text("/u/Udzu", arial(16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)

img.save(f"output/euboris.png")

