from pudzu.charts import *
from pudzu.bamboo import *

fg, bg="black", "white"
COLS = 5
default_img = "https://s-media-cache-ak0.pinimg.com/736x/0d/36/e7/0d36e7a476b06333d9fe9960572b66b9.jpg"

flags = pd.read_csv("datasets/countries.csv").split_columns(('nationality', 'tld', 'country'), "|").explode('country').set_index('country')['flag']
flags["EU"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b7/Flag_of_Europe.svg/1024px-Flag_of_Europe.svg.png"
flags["UN"] = 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Flag_of_the_United_Nations.svg/1024px-Flag_of_the_United_Nations.svg.png'

def half_and_half(img1, img2):
    assert img1.size == img2.size
    w, h = (wh - 1 for wh in img1.size)
    mask_array = np.fromfunction(lambda y,x: h-(h*x)/w >= y, tuple(reversed(img1.size)))
    mask = Image.fromarray(mask_array * 255).convert("1")
    return img2.overlay(img1, mask=mask, copy=True)

def horizontal_combo(imgs):
    assert all(img.size == imgs[0].size for img in imgs)
    w, n = imgs[0].width, len(imgs)
    combo = imgs[0]
    for i, img in enumerate(imgs[1:], 1):
        mask_array = 1 - np.fromfunction(lambda y,x: (i * (w / n) <= x) * (x < (i + 1) * (w / n)), tuple(reversed(imgs[0].size)))
        mask = Image.fromarray(mask_array * 255).convert("1")
        combo = img.overlay(combo, mask=mask, copy=True)
    return combo
    
def make_flag(countries):
    flagimgs = [Image.from_url_with_cache(get_non(flags, country, default_img)).convert("RGB").resize((300, 180)) for country in countries]
    if len(flagimgs) == 2: flagimg = half_and_half(*flagimgs)
    else: flagimg = horizontal_combo(flagimgs)
    return flagimg.resize_fixed_aspect(width=60).trim(1).pad(1, "grey")

def split_rows(array, n):
    pad = len(array[0])
    split = list(generate_batches(array, n))
    return list(map(artial(sum, []), zip_longest(*split, fillvalue=[None]*pad)))

for source in ["eusites_moz", "eusites_alexa"]: # Alexa list from http://rpki.surfnet.nl/top500.php

    df = pd.read_csv("datasets/{}.csv".format(source)).split_columns(('country'), "|")

    array = [[
        make_flag(get_non(d, 'country')),
        Image.from_url_with_cache(get_non(d, 'logo', default_img)).pad_to_aspect(4, 3, bg="white").resize_fixed_aspect(width=100),
        Image.from_column([
            Image.from_text("{}. {}".format(d['rank'], d['domain'].upper()), arial(20, bold=True), fg=fg, bg=bg, padding=(0,1)),
            Image.from_text(get_non(d, 'description', '??'), arial(16), fg=fg, bg=bg, padding=(0,1))
        ], xalign=0, bg="white").pad((0,0,10,0), "white")
        ]
        for _, d in df.iterrows()]
        
    array = split_rows(array, math.ceil(len(array)/COLS))
    grid = Image.from_array(array, bg=bg, padding=(8,10), xalign=(0,0,0,0)*COLS).pad((5,0), bg=bg)

    # TODO: titles/footers (based in; e.g. xhamster  
    if source == "eusites_moz":
        title = Image.from_column([
            Image.from_text("50 most important European websites according to Moz".upper(), arial(72, bold=True), fg=fg, bg=bg),
            Image.from_text("European-founded or owned web domains in Moz's Top 500 list, based on number of linking root domains", arial(48, italics=True), fg=fg, bg=bg).pad(5,bg=bg)
            ], bg=bg)
        footer = Image.from_text("(excludes foreign sites based in Europe such as google.de; sites marked with an * also appear further down the list under additional domain names)", arial(24), fg=fg, bg=bg, padding=2)
    else:
        title = Image.from_column([
            Image.from_text("50 most popular European websites according to Alexa".upper(), arial(72, bold=True), fg=fg, bg=bg),
            Image.from_text("European-founded or owned web domains in Alexa's Top 500 list; excludes foreign sites based in Europe", arial(48, italics=True), fg=fg, bg=bg).pad(5,bg=bg)
            ], bg=bg)
        footer = Image.EMPTY_IMAGE

    img = Image.from_column([title, grid, footer], bg=bg, padding=(0,10))
    img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
    img.save("output/{}.png".format(source))
