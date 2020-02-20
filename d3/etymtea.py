from pudzu.charts import *
from generate import *


FONT = sans
DEFAULT = VegaPalette10.GREEN
PALETTE = { 
"t": VegaPalette10.RED, 
"ot": VegaPalette10.PINK,
"c": VegaPalette10.BLUE,
"oc": VegaPalette10.LIGHTBLUE,
"o": VegaPalette10.BROWN,
 }
PATTERNS = ""

df = pd.read_csv("datasets/etymtea.csv").set_index("country")

# TODO: move this logic elsewhere
WIDTH = 4
for c, r in df.iterrows():
    p = r.category
    if isinstance(p, str) and p not in PALETTE:
        ps = p.split("|")
        if all(p in PALETTE for p in ps):
            rects = [f'<rect x="{i*WIDTH}" y="0" width="{WIDTH}" height="{WIDTH*len(ps)}" style="fill:{PALETTE[p].to_hex()}"/>' for i,p in enumerate(ps)]
            PATTERNS += f'''<defs>
  <pattern id="{''.join(ps)}" width="{WIDTH*len(ps)}" height="{WIDTH*len(ps)}" patternTransform="rotate(45 0 0)" patternUnits="userSpaceOnUse">
    {'  '.join(rects)}
  </pattern>
</dev>
'''
            PALETTE[p] = f'url(#{"".join(ps)})'
    if p not in PALETTE: print(c, p)

assert set(df.index) < set(atlas.index), f'Unrecognised countries: {set(df.index) - set(load_name_csv("../dataviz/maps/World.png").name)}'

# TODO: stripes
colormap = { c: df.category[c] if df.category[c] in PALETTE else "o" for c in df.index }
generate_datamap("etymtea", colormap, palette=PALETTE, patterns=PATTERNS, codifier=partial(codify_countries, dependencies=False))
