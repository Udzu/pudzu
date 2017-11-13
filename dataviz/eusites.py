import sys
sys.path.append('..')
from charts import *
from bamboo import *

fg, bg="black", "white"
COLS = 5
default_img = "https://s-media-cache-ak0.pinimg.com/736x/0d/36/e7/0d36e7a476b06333d9fe9960572b66b9.jpg"

df = pd.read_csv("datasets/eusites.csv").split_columns(('country'), "|")
flags = pd.read_csv("datasets/countries.csv").split_columns(('nationality', 'tld', 'country'), "|").split_rows('country').set_index('country')['flag']
flags["EU"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b7/Flag_of_Europe.svg/1024px-Flag_of_Europe.svg.png"
flags["Nordic"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e2/Coa_Illustration_Cross_Sideways.svg/1024px-Coa_Illustration_Cross_Sideways.svg.png"

# TODO: flg combo, nordic flag

def half_and_half(img1, img2):
    assert img1.size == img2.size
    w, h = (wh - 1 for wh in img1.size)
    mask_array = np.fromfunction(lambda y,x: h-(h*x)/w >= y, tuple(reversed(img1.size)))
    mask = Image.fromarray(mask_array * 255).convert("1")
    return img2.overlay(img1, mask=mask, copy=True)

def make_flag(countries):
    flagimgs = [Image.from_url_with_cache(get_non(flags, country, default_img)).convert("RGB").resize((300, 180)) for country in countries]
    if len(flagimgs) == 1: flagimg = flagimgs[0]
    else: flagimg = half_and_half(*flagimgs)
    return flagimg.resize_fixed_aspect(width=60).trim(1).pad(1, "grey")

array = [[
    make_flag(get_non(d, 'country')),
    Image.from_url_with_cache(get_non(d, 'logo', default_img)).pad_to_aspect(1, bg="white").resize_fixed_aspect(width=100),
    Image.from_column([
        Image.from_text("{}. {}".format(d['rank'], d['domain'].upper()), arial(20, bold=True), fg=fg, bg=bg, padding=(0,1)),
        Image.from_text(get_non(d, 'description', '??')+".", arial(16), fg=fg, bg=bg, padding=(0,1))
    ], xalign=0, bg="white").pad((0,0,10,0), "white")
    ]
    for _, d in df.iterrows()]
    
def split_rows(array, n):
    pad = len(array[0])
    split = list(generate_batches(array, n))
    return list(map(artial(sum, []), zip_longest(*split, fillvalue=[None]*pad)))
    
array = split_rows(array, math.ceil(len(array)/COLS))
grid = Image.from_array(array, bg=bg, padding=(8,10), xalign=(0,0,0,0)*COLS).pad((5,0), bg=bg)

title = Image.from_column([
    Image.from_text("50 most important European websites according to Moz".upper(), arial(72, bold=True), fg=fg, bg=bg),
    Image.from_text("European-founded or owned web domains in Moz's Top 500 list, based on number of linking root domains", arial(48, italics=True), fg=fg, bg=bg).pad(5,bg=bg)
    ], bg=bg)
      
img = Image.from_column([title, grid], bg=bg, padding=(0,10))
img.save("output/eusites.png")
