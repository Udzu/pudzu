from pudzu.charts import *
from pudzu.bamboo import *

flags = pd.read_csv("../dataviz/datasets/countries.csv").filter_rows("organisations >> un").split_columns('country', "|").split_rows('country').set_index('country').drop_duplicates(subset='flag', keep='first')

def flag_image(c):
    return Image.from_url_with_cache(flags['flag'][c]).convert("RGBA").remove_transparency("white").convert("RGB")
    
def average_image(imgs, size, weights=None):
    if weights is None: weights = [1 for _ in imgs]
    average = ImageColor.from_linear(sum(ImageColor.to_linear(np.array(img.resize(size))) * w for img,w in zip(imgs, weights)) / sum(weights))
    return Image.fromarray(np.uint8(average))

def average_flag(df, size, weights=None):
    if callable(weights): weights = weights(df)
    flags = [flag_image(i) for i in df.index]
    return average_image(flags, (size[0]-2,size[1]-2), weights).pad(1, "black")
    
continents = flags.groupby("continent").count().index
continentlabels = [ Image.from_text(continent.upper(), calibri(60, bold=True), "black", "white")  for continent in continents ]
    
world = average_flag(flags, (1200,800))
world_weighted = average_flag(flags, (1200,800), lambda df: df.population)
continent = Image.from_array([continentlabels, [average_flag(flags[flags.continent == continent], (600, 400)) for continent in continents]], padding=5, bg="white")
continent_weighted = Image.from_array([continentlabels, [average_flag(flags[flags.continent == continent], (600, 400), lambda df: df.population) for continent in continents]], padding=5, bg="white")

os.makedirs("output/averageflags", exist_ok=True)
world.save("output/averageflags/world.png")
world_weighted.save("output/averageflags/world_weighted.png")
continent.save("output/averageflags/continents.png")
continent_weighted.save("output/averageflags/continents_weighted.png")

# quick and dirty scrape of some area data: will add to the country dataset at some point

df = pd.read_html("https://en.wikipedia.org/wiki/List_of_countries_and_dependencies_by_area")[0]
df = df.rename(columns=df.iloc[0])[1:].fillna("0")
df = df.assign_rows(country=lambda d: d[next(c for c in df.columns if "state" in c)].split(" (")[0].split(" !")[-1].strip(" \xa0"),
                    area=lambda d: d[next(c for c in df.columns if "Total" in c)].split(" (")[0].split(chr(9824))[1].replace(",","").replace("<","")).set_index("country")
flags = flags.assign_rows(area=lambda d,c: df["area"][c]).apply(pd.to_numeric, errors='ignore')

world_area = average_flag(flags, (1200,800), lambda df: df.area)
world_area.save("output/averageflags/world_area.png")
world_density = average_flag(flags, (1200,800), lambda df: df.population / df.area)
world_density.save("output/averageflags/world_density.png")

continent_area = Image.from_array([continentlabels, [average_flag(flags[flags.continent == continent], (600, 400), lambda df: df.area) for continent in continents]], padding=5, bg="white")
continent_area.save("output/averageflags/continents_area.png")
continent_density = Image.from_array([continentlabels, [average_flag(flags[flags.continent == continent], (600, 400), lambda df: df.population / df.area) for continent in continents]], padding=5, bg="white")
continent_density.save("output/averageflags/continents_density.png")
