from pudzu.charts import *
from generate import *

mottos = pd.read_csv("../dataviz/datasets/usmottos.csv").set_index("state")
states = pd.read_csv("../dataviz/datasets/usstates.csv").set_index("code").join(mottos, on="name").fillna(" ")
flags = states.flag

DATAMAP = { }
PATTERNS = ""
WIDTH = 10
LABELS = None

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

generate_datamap("flagsmodeus", DATAMAP, patterns=PATTERNS, labels=LABELS, geography={"borderWidth": 1.0, "borderColor": "#000000"}, 
                 map_path="libraries/datamaps.usa.min.js", width=2000, scope="usa", codifier=None
)

map = Image.open("temp/flagsmodeus.png")
title = Image.from_text("Modal US state flag colours".upper(), arial(96, bold=True), padding=(0,0,0,2))
subtitle = Image.from_text("most common colour per flag, based on images from Wikipedia", arial(60, italics=True), padding=(0,0,0,2))
img = Image.from_column([title, subtitle, map], padding=8, bg="white")
img.place(Image.from_text("/u/Udzu", font("arial", 24), fg="black", bg=None, padding=10).pad((2,2,0,0), "black"), align=1, padding=20, copy=False)
img.save("output/flagsmodeusmap.png")
