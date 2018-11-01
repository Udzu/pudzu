from pudzu.charts import *
from generate import *
from statistics import mean

flags = pd.read_csv("../dataviz/datasets/countries.csv").split_columns(('country'), "|").split_rows('country').set_index('country').flag
flags["northern_cyprus"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Flag_of_the_Turkish_Republic_of_Northern_Cyprus.svg/1024px-Flag_of_the_Turkish_Republic_of_Northern_Cyprus.svg.png"
flags["somaliland"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/Flag_of_Somaliland.svg/1024px-Flag_of_Somaliland.svg.png"

def to_linear(srgb):
    c = srgb / 255
    return np.where(c <= 0.04045, c / 12.92, ((c+0.055)/1.055)**2.4)

def from_linear(lrgb):
    c = np.where(lrgb <= 0.0031308, 12.92 * lrgb, (1.055)*lrgb**(1/2.4)-0.055)
    return np.round(c * 255)

def colorfn(c):
    if c not in flags.index: return "white" if c in ['Sea', 'Borders'] else "grey"
    flag_array = np.array(Image.from_url_with_cache(flags[c]).convert("RGB"))
    float_average = [ from_linear(to_linear(flag_array[:,:,i]).mean()) for i in range(flag_array.shape[-1])]
    return RGBA([int(f) for f in float_average])

colormap = { k : colorfn(k) for k in flags.index }
generate_datamap("flagsaverage", colormap)

map = Image.open("temp/flagsaverage.png")
title = Image.from_text("Average flag colours of the world".upper(), arial(96, bold=True), padding=(0,0,0,2))
subtitle = Image.from_text("calculated from flag images on Wikipedia, averaged using sRGB gamma-correction", arial(60, italics=True), padding=(0,0,0,2))
img = Image.from_column([title, subtitle, map], padding=8, bg="white")
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/flagsaveragemap.png")
