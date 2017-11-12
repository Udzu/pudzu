import sys
sys.path.append('..')
from charts import *
from bamboo import *

df = pd.read_csv("datasets/flagsuk.csv")
fg, bg="black", "white"
default_img = "https://s-media-cache-ak0.pinimg.com/736x/0d/36/e7/0d36e7a476b06333d9fe9960572b66b9.jpg"

array = [[
    Image.from_column([
        Image.from_text(d['country'], arial(48, bold=True), fg=fg, bg=bg, align="center", max_width=400),
        Image.from_text("({})".format(d['dates']), arial(48, bold=False), fg=fg, bg=bg)
    ], bg=bg, padding=(0,5)),
    Image.from_url_with_cache(d['flag']).resize((318,198)).pad(1, "grey"),
    Image.from_text(get_non(d, 'description', 'f'), arial(48), fg=fg, bg=bg, max_width=1000, padding=(0,4,0,8))
    ]
    for _, d in df.iterrows()]

flags =  Image.from_array(array, bg=bg, padding=(10,20), xalign=(0.5,0,0)).pad((5,0), bg=bg)

title = Image.from_column([
    Image.from_text("Variations on a theme".upper(), arial(72, bold=True), fg=fg, bg=bg),
    Image.from_text("8 flags that contain the Union Jack (and 1 that doesn't) ", arial(48, italics=True), fg=fg, bg=bg).pad(5,bg=bg)
    ], bg=bg)
      
img = Image.from_column([title, flags], bg=bg, padding=(0,10))
img.save("output/flagsuk.png")
