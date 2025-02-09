from pudzu.charts import *
from pudzu.pillar import *
from pudzu.sandbox.bamboo import *

df = pd.read_csv("datasets/gerontocracy.csv")
flags = pd.read_csv("../dataviz/datasets/countries.csv").split_columns(('country'), "|").explode('country').set_index('country').flag
default_img = "https://s-media-cache-ak0.pinimg.com/736x/0d/36/e7/0d36e7a476b06333d9fe9960572b66b9.jpg"

def cell(s):
    flag = Image.from_url_with_cache(flags[s.country]).to_rgba().resize((318,198)).pad(1, "grey")
    name = Image.from_markup(f"**{s['name']}** ({s.age})", partial(sans, 24), padding=(0, 10), fg="white")
    portrait = Image.from_url_with_cache(get_non(s, "image", default_img)).crop_to_aspect(100, 100, (get_non(s, "crop", 0.5), get_non(s, "crop", 0.2))).resize_fixed_aspect(width=320)
    return Image.from_column([
        flag,
        portrait,
        name,
    ])

cells = [cell(s) for _, s in df.iterrows()]
grid = Image.from_array(list(generate_batches(cells, 4)), padding=0, bg="black")
title = Image.from_text_bounded("geopolitical gerontocracy".upper(), grid.size, 92, papply(sans, bold=True), padding=2, fg="white")
subtitle = Image.from_text_bounded("the dominance of old men in the world's political hotspots", grid.size, 64, papply(sans, italics=True), padding=2, fg="white")
img = Image.from_column([title, subtitle, Rectangle((0,15)), grid], bg="black").pad(25, "black")
img.convert("RGB").save("output/genotocracy.jpg")