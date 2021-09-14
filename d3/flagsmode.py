from pudzu.charts import *
from generate import *

flags = pd.read_csv("../dataviz/datasets/countries.csv").split_columns(('country'), "|").explode('country').set_index('country').flag
flags["northern_cyprus"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Flag_of_the_Turkish_Republic_of_Northern_Cyprus.svg/1024px-Flag_of_the_Turkish_Republic_of_Northern_Cyprus.svg.png"
flags["somaliland"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/Flag_of_Somaliland.svg/1024px-Flag_of_Somaliland.svg.png"
flags["Afghanistan"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/2/24/Flag_of_Taliban.svg/1024px-Flag_of_Taliban.svg.png"
flags["Saint Barthélemy"] = flags["France"]

DATAMAP = { }
PATTERNS = ""
WIDTH = 10

for c in flags.index:
    flag = Image.from_url_with_cache(flags[c]).convert("RGBA")
    colors = sorted((c for c  in flag.getcolors(65536) if c[1][-1] == 255), reverse=True)
    best = [RGBA(c) for x,c in colors if x / colors[0][0] > 0.99]
    if len(best) == 1:
        DATAMAP[c] = best[0]
    else:
        key = "".join(c.to_hex().replace("#","") for c in best)
        DATAMAP[c] = f'url(#{key})'
        rects = [f'<rect x="{i*WIDTH}" y="0" width="{WIDTH}" height="{WIDTH*len(best)}" style="fill:{c.to_hex()}"/>' for i,c in enumerate(best)]
        PATTERNS += f'''<defs>
  <pattern id="{key}" width="{WIDTH*len(best)}" height="{WIDTH*len(best)}" patternTransform="rotate(45 0 0)" patternUnits="userSpaceOnUse">
    {'  '.join(rects)}
  </pattern>
</dev>
'''

generate_datamap("flagsmode", DATAMAP, patterns=PATTERNS, geography={"borderWidth": 1.0, "borderColor": "#000000"})

map = Image.open("temp/flagsmode.png") # save at 150%
title = Image.from_text("Modal flag colours of the world".upper(), arial(144, bold=True), padding=(0,0,0,3))
subtitle = Image.from_text("most common colour on every flag, calculated from images on Wikipedia", arial(90, italics=True), padding=(0,0,0,3))
img = Image.from_column([title, subtitle, map], padding=12, bg="white")
img.place(Image.from_text("/u/Udzu", font("arial", 32), fg="black", bg=None, padding=10).pad((2,2,0,0), "black"), align=1, padding=20, copy=False)
img.save("output/flagsmodemap.png")
