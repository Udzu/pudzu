from pudzu.charts import *
from pudzu.bamboo import *

flags = pd.read_csv("datasets/countries.csv")[lambda df: df.code != "EUU"].split_columns(('nationality', 'tld', 'country'), "|").split_rows('country').set_index('country').drop_duplicates(subset='flag', keep='first')
bg = "#EEEEEE"

def image_flag(c):
    return Image.from_url_with_cache(flags['flag'][c]).convert("RGB")
    
def average_color(img):
    float_array = np.array(img) / 256
    float_average = [ math.sqrt((float_array[:,:,i] ** 2).mean()) for i in range(float_array.shape[-1])]
    return RGBA(int(256 * f) for f in float_average)

def average_image(imgs, size, weights=None):
    if weights is None: weights = [1 for _ in imgs]
    average = (sum((np.array(img.resize(size)) / 256)**2 * w for img,w in zip(imgs, weights)) / sum(weights)) ** 0.5
    return Image.fromarray(np.uint8(average * 256))

def average_flag(df, size, weights=None):
    if callable(weights): weights = weights(df)
    flags = [Image.from_url_with_cache(i).convert("RGB") for i in df.flag]
    return average_image(flags, (size[0]-2,size[1]-2), weights).pad(1, "black")

continents = list(flags.groupby("continent").count().index)
continentlabels = [ Image.from_text(continent.upper(), arial(60, bold=True), "black", bg)  for continent in continents ]

imgs = []

for weights, TITLE, SUBTITLE in [(None, "AVERAGE WORLD/CONTINENT FLAGS", "averages of aspect-normalised state & dependency flags"),
                                 (lambda df: df.population, "WEIGHTED AVERAGE FLAGS", "same, but weighted by population")]:
    world = average_flag(flags, (1200,800), weights=weights)
    continentflags = [ average_flag(flags[flags.continent == continent], (630,420), weights=weights) for continent in continents ]
    continentimgs = [ Image.from_column([label, flag], padding=10) for flag, label in zip(continentflags, continentlabels) ]
    continentarray = Image.from_array(list(generate_batches(continentimgs, 3)), bg=bg, padding=5, yalign=1)
    subtitle = Image.from_text(SUBTITLE, arial(60, bold=True), "black", bg, padding=(0,0,0,20))
    title = Image.from_column([Image.from_text(TITLE, arial(96, bold=True), "black", bg), subtitle], bg=bg, padding=10)
    img = Image.from_column([title, world, continentarray], bg=bg, padding=20)
    imgs.append(img)

FOOTER = "*each flag is assigned to just one continent; average is the quadratic mean of RGB values (as per the Computer Color is Broken Youtube video)"
footer = Image.from_text(FOOTER, arial(48), "black", bg, padding=10)
img = Image.from_column([Image.from_row(imgs, yalign=0), footer], bg=bg, padding=20)
img.place(Image.from_text("/u/Udzu", font("arial", 32), fg="black", bg=bg, padding=10).pad((2,2,0,0), "black"), align=1, padding=20, copy=False)
img.save("output/flagsaverage.jpg")

