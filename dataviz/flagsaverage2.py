from pudzu.charts import *
from pudzu.experimental.bamboo import *
import scipy.stats

flags = pd.read_csv("../dataviz/datasets/countries.csv").filter_rows("organisations >> un").split_columns('country', "|").explode('country').set_index('country').drop_duplicates(subset='flag', keep='first')
continents = flags.groupby("continent").count().index

SIZE = 100
FLAG_WIDTH = 6*SIZE
BOX_WIDTH = SIZE * 3 // 4
LABEL_FONT = calibri(SIZE, bold=True)
SUB_FONT = partial(calibri, SIZE*2//3)

def flag_image(c):
    return Image.from_url_with_cache(flags['flag'][c]).convert("RGBA").remove_transparency("white").convert("RGB")
    
def label_image(text, align="center"):
    return Image.from_text(text.upper().replace(" ","\n"), LABEL_FONT, "black", "white", align=align)

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
    mode = Image.fromarray(scipy.stats.mode(a, -1)[0][...,0], "P")
    mode.putpalette(list(generate_leafs(RGBA(col)[:3] for col in list(HeraldicPalette))))
    return mode.to_rgba()

def median_image(imgs, size):
    a = np.stack([np.array(img.convert("L").resize(size)) for img in imgs], axis=-1)
    median = np.median(a, axis=-1)
    return Image.fromarray(np.uint8(median), "L").to_rgba()
    
def median_image_rgb(imgs, size):
    imgs = [img.resize(size) for img in imgs]
    arrays = [np.stack([np.array(img.getchannel(i)) for img in imgs], axis=-1) for i in range(3)]
    medians = [Image.fromarray(np.uint8(np.median(a, axis=-1)), "L") for a in arrays]
    return Image.merge("RGB", medians)
    
def average_flag(df, size, average):
    flags = [flag_image(i) for i in df.index]
    return average(flags, (size[0]-2,size[1]-2)).pad(1, "black")
    
def average_flags(label, average):
    world = average_flag(flags, (FLAG_WIDTH, FLAG_WIDTH*2//3), average)
    continent = [average_flag(flags[flags.continent == continent], (FLAG_WIDTH, FLAG_WIDTH*2//3), average) for continent in continents]
    return [label_image(label), world] + continent

array = [[None, label_image("world")] + [label_image(c) for c in continents],
         average_flags("mean", mean_image),
         average_flags("mode", mode_image),
         average_flags("median", median_image_rgb)]
grid = Image.from_array(tmap(list, zip(*array)), bg="white", padding=SIZE // 5, xalign=(1,0.5,0.5,0.5,0.5))
         
title = Image.from_column([
  Image.from_text("Average flags of the world".upper(), calibri(SIZE*2, bold=True), "black", "white"),
  Image.from_text("mean versus mode versus median", calibri(SIZE*3//2, italics=True), "black", "white")
], padding=SIZE//10)
descriptions = [
    Image.from_markup("Averages flags of the 195 member and observer states of the UN, resized to a constant aspect ratio.", SUB_FONT),
    Image.from_markup("**Mean flags** calculated by first converting from sRGB to linear RGB.", SUB_FONT),
    Image.from_row([
        Image.from_markup("**Modal flags** calculated by first quantizing to heraldic colors: ", SUB_FONT),
        Checkers((BOX_WIDTH*len(HeraldicPalette), BOX_WIDTH), GradientColormap(*HeraldicPalette), shape=(len(HeraldicPalette), 1), colors=len(HeraldicPalette)).add_grid((len(HeraldicPalette), 1))]),
    Image.from_markup("**Median flags** calculated separately for each RGB channel.", SUB_FONT)]
img = Image.from_column([title, Image.from_column(descriptions, equal_heights=True, xalign=0), grid], padding=SIZE//4, bg="white")
img.place(Image.from_text("/u/Udzu", font("arial", 40), fg="black", bg="white", padding=10).pad((2,2,0,0), "black"), align=1, padding=20, copy=False)
img.save("output/flagsaverage2.png")

# Extras
# array = [[None, label_image("world")] + [label_image(c, "right") for c in continents], average_flags("RGB median", median_image_rgb)]
# grid = Image.from_array(tmap(list, zip(*array)), bg="white", padding=SIZE // 5, xalign=(1,0.5))

