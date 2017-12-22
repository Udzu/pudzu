import sys
sys.path.append('..')
from charts import *
from statistics import mean

countries = pd.read_csv("datasets/countries.csv").split_columns(('country'), "|").split_rows('country').set_index('country')
states = pd.read_csv("datasets/usstates.csv").set_index('name')

def to_linear(srgb):
    c = srgb / 255
    return np.where(c <= 0.04045, c / 12.92, ((c+0.055)/1.055)**2.4)

def from_linear(lrgb):
    c = np.where(lrgb <= 0.0031308, 12.92 * lrgb, (1.055)*lrgb**(1/2.4)-0.055)
    return np.round(c * 255)

def colorfn(c, flags, *args):
    if c not in flags.index: return "white" if c in ['Sea', 'Borders'] else "grey"
    flag_array = np.array(Image.from_url_with_cache(flags['flag'][c]).convert("RGB"))
    float_average = [ from_linear(to_linear(flag_array[:,:,i]).mean()) for i in range(flag_array.shape[-1])]
    return ImageColor.getrgba(int(f) for f in float_average)

map1 = map_chart("maps/Europe.png", artial(colorfn, countries))
map2 = map_chart("maps/USA.png", artial(colorfn, states))

title = Image.from_text("Average flag colours of Europe and the USA".upper(), arial(96, bold=True), padding=(0,0,0,2))
subtitle = Image.from_text("calculated from flag images on Wikipedia, averaged using sRGB gamma-correction", arial(60, italics=True), padding=(0,0,0,2))
img = Image.from_column([title, subtitle, Image.from_row([map2, map1])], padding=8, bg="white")
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/flagsaveragemap.png")


