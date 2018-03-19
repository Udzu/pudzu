import sys
sys.path.append('..')
from charts import *
from bamboo import *
import scipy.stats

flags = pd.read_csv("../dataviz/datasets/countries.csv").filter_rows("organisations >> un").split_columns('country', "|").split_rows('country').set_index('country').drop_duplicates(subset='flag', keep='first')
continents = flags.groupby("continent").count().index

SIZE = 20 # 4 / 20
WIDTH = 30*SIZE
LABEL_FONT = calibri(5*SIZE, bold=True)

def flag_image(c):
    return Image.from_url_with_cache(flags['flag'][c]).convert("RGBA").remove_transparency("white").convert("RGB")
    
def label_image(text):
    return Image.from_text(text.upper(), LABEL_FONT, "black", "white")

def mean_image(imgs, size):
    average = ImageColor.from_linear(sum(ImageColor.to_linear(np.array(img.resize(size))) for img in imgs) / len(imgs))
    return Image.fromarray(np.uint8(average))

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

def mode_image(imgs, size):
    a = np.stack([np.array(img.to_palette(HeraldicPalette).resize(size)) for img in imgs], axis=-1)
    mode = scipy.stats.mode(a, -1)[0][...,0]
    img = Image.fromarray(mode, "P")
    img.putpalette(list(generate_leafs(RGBA(col)[:3] for col in list(HeraldicPalette))))
    return img.to_rgba()

def median_image(imgs, size):
    a = np.stack([np.array(img.convert("L").resize(size)) for img in imgs], axis=-1)
    median = np.median(a, axis=-1)
    return Image.fromarray(np.uint8(median), "L").to_rgba()
    
def average_flag(df, size, average):
    flags = [flag_image(i) for i in df.index]
    return average(flags, (size[0]-2,size[1]-2)).pad(1, "black")
    
def average_flags(label, average):
    world = average_flag(flags, (WIDTH, WIDTH*2//3), average)
    continent = [average_flag(flags[flags.continent == continent], (WIDTH, WIDTH*2//3), average) for continent in continents]
    return [label_image(label), world] + continent

array = [[None, label_image("world")] + [label_image(c) for c in continents],
         average_flags("mean", mean_image),
         average_flags("mode", mode_image),
         average_flags("median", median_image)]
grid = Image.from_array(tmap(list, zip(*array)), bg="white", padding=SIZE, xalign=(1,0.5,0.5,0.5,0.5))
         
# TODO: legend, title, etc