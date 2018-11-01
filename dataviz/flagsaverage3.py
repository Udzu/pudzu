from pudzu.charts import *
from pudzu.bamboo import *
import scipy.stats

flags = pd.read_csv("../dataviz/datasets/countries.csv").filter_rows("organisations >> un").split_columns('country', "|").split_rows('country').set_index('country').drop_duplicates(subset='flag', keep='first')
continents = flags.groupby("continent").count().index

df = pd.read_html("https://en.wikipedia.org/wiki/List_of_countries_and_dependencies_by_area")[0]
df = df.rename(columns=df.iloc[0])[1:].fillna("0")
df = df.assign_rows(country=lambda d: d[next(c for c in df.columns if "state" in c)].split(" (")[0].split(" !")[-1].strip(" \xa0"),
                    area=lambda d: d[next(c for c in df.columns if "Total" in c)].split(" (")[0].split(chr(9824))[1].replace(",","").replace("<","")).set_index("country")
flags = flags.assign_rows(area=lambda d,c: df["area"][c]).apply(pd.to_numeric, errors='ignore')

SIZE = 100
FLAG_WIDTH = 6*SIZE
BOX_WIDTH = SIZE * 3 // 4
LABEL_FONT = calibri(SIZE, bold=True)
SUB_FONT = partial(calibri, SIZE*2//3)

def flag_image(c):
    return Image.from_url_with_cache(flags['flag'][c]).convert("RGBA").remove_transparency("white").convert("RGB")
    
def label_image(text, align="center"):
    return Image.from_text(text.upper().replace(" ","\n").replace("NORTH","NORTH &\nCENTRAL"), LABEL_FONT, "black", "white", align=align)

class HeraldicPalette(metaclass=NamedPaletteMeta):
    # Omits Murrey and Sanguine (which are very similar to Gules and Purpure) and Cendree and Carnation (which are barely used).
    OR = "#fcdd09"
    ARGENT = "#ffffff"
    AZURE = "#0f47af"
    GULES = "#da121a"
    PURPURE = "#9116a1"
    SABLE = "#000000"
    VERT = "#009200"
    TENNE = "#804000"
    ORANGE = "#ff8000"
    CELESTE = "#75aadb"

def mean_weighted(imgs, size, weights):
    average = ImageColor.from_linear(sum(ImageColor.to_linear(np.array(img.resize(size)))*w for img,w in zip(imgs, weights)) / sum(weights))
    return Image.fromarray(np.uint8(average))

def mode_weighted(imgs, size, weights):
    arrays = [np.array(img.to_palette(HeraldicPalette).resize(size)) for img in imgs]
    totals = np.stack([sum((a==c)*w for a,w in zip(arrays, weights)) for c in range(len(HeraldicPalette))], axis=0)
    mode = np.argmax(totals, axis=0)
    mode = Image.fromarray(np.uint8(mode), "P")
    mode.putpalette(list(generate_leafs(RGBA(col)[:3] for col in list(HeraldicPalette))))
    return mode.to_rgba()
    
def average_weighted(df, size, average, weight_fn):
    flags = [flag_image(i) for i in df.index]
    weights = [weight_fn(i) for i in df.index]
    return average(flags, (size[0]-2,size[1]-2), weights).pad(1, "black")

def average_flags(label, average, weight_fn):
    world = average_weighted(flags, (FLAG_WIDTH, FLAG_WIDTH*2//3), average, weight_fn)
    continent = [average_weighted(flags.filter_rows(lambda d,i: d['continent'] == continent or i == "Russia" and continent == "Asia"), (FLAG_WIDTH, FLAG_WIDTH*2//3), average, partial(weight_fn, c=continent)) for continent in continents]
    return [label_image(label), world] + continent

def by_country(i, c=None): return 1
def by_population(i, c=None): return [110000000,35000000][c == "Asia"] if i == "Russia" and c is not None else flags.population[i]
def by_area(i, c=None):return [4275000,12825000][c == "Asia"] if i == "Russia" and c is not None else int(flags.area[i])

array = [[None, label_image("world")] + [label_image(c, "right") for c in continents],
         average_flags("mean", mean_weighted, by_country),
         average_flags("(population weighted)", mean_weighted, by_population),
         average_flags("(area weighted)", mean_weighted, by_area),
         average_flags("mode", mode_weighted, by_country),
         average_flags("(population weighted)", mode_weighted, by_population),
         average_flags("(area weighted)", mode_weighted, by_area)]
grid = Image.from_array(tmap(list, zip(*array)), bg="white", padding=SIZE // 5, xalign=(1,0.5,0.5,0.5,0.5,0.5,0.5))
         
title = Image.from_column([
  Image.from_text("Average flags of the world".upper(), calibri(SIZE*2, bold=True), "black", "white"),
  Image.from_text("mean and mode, weighted by population and area", calibri(SIZE*3//2, italics=True), "black", "white")
], padding=SIZE//10)
descriptions = [
    Image.from_markup("Averages flags of the 195 member and observer states of the UN, resized to a constant aspect ratio.", SUB_FONT),
    Image.from_markup("**Mean flags** calculated by converting from sRGB to linear RGB, averaging, and converting back.", SUB_FONT),
    Image.from_row([
        Image.from_markup("**Modal flags** calculated pixelwise by first quantizing to heraldic colors: ", SUB_FONT),
        Checkers((BOX_WIDTH*len(HeraldicPalette), BOX_WIDTH), GradientColormap(*HeraldicPalette), shape=(len(HeraldicPalette), 1), colors=len(HeraldicPalette)).add_grid((len(HeraldicPalette), 1))])]
img = Image.from_column([title, Image.from_column(descriptions, equal_heights=True, xalign=0), grid], padding=SIZE//4, bg="white")
img.place(Image.from_text("/u/Udzu", font("arial", 40), fg="black", bg="white", padding=10).pad((2,2,0,0), "black"), align=1, padding=20, copy=False)
img.save("output/flagsaverage3.png")

# Extras
# countries = ["Mexico", "Germany", "New Zealand"]
# array = ([[None] + [label_image(c) for c in countries]] +
         # [[label_image(l)] + [average_weighted(flags.filter_rows(lambda d: d['continent'] == flags.continent[c]), (FLAG_WIDTH, FLAG_WIDTH*2//3), mean_weighted, lambda country: (i if c == country else 1) * by_population(country, flags.continent[c])) for c in countries] for l,i in [("without", 0), ("with", 1), ("boosted×5", 5)]])
# grid = Image.from_array(tmap(list, zip(*array)), bg="white", padding=SIZE // 5, xalign=(1,0.5,0.5,0.5,0.5,0.5,0.5))

# flags = pd.read_csv("../dataviz/datasets/usstates.csv").set_index('name')
# df = pd.read_html("https://en.wikipedia.org/wiki/List_of_U.S._states_and_territories_by_area")[0]
# df = df.rename(columns=df.iloc[1])[2:].fillna("0")
# df.columns = range(len(df.columns))
# df = df.set_index(0)
# flags = flags.assign_rows(area=lambda d,c: df[2][c]).apply(pd.to_numeric, errors='ignore')
# array = [[label_image(l) for l in ["mean", "(population weighted)", "(area weighted)", "mode", "(population weighted)", "(area weighted)"]],
         # [average_weighted(flags, (FLAG_WIDTH, FLAG_WIDTH*2//3), average, weighting) for (average, weighting) in zip([mean_weighted]*3+[mode_weighted]*3, [by_country,by_population, by_area]*2)]]
# grid = Image.from_array(array, bg="white", padding=SIZE // 5, xalign=0.5)
