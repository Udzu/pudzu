from pudzu.charts import *
from generate import *

# t: from te
# ot: + other morpheme: dute, herbata
# c: from cha
# oc: + other morpheme

FONT = sans
DEFAULT = VegaPalette10.GREEN
PALETTE = { 
"t": VegaPalette10.RED, 
"ot": VegaPalette10.PINK,
"c": VegaPalette10.BLUE,
"oc": VegaPalette10.LIGHTBLUE,
"o": VegaPalette10.ORANGE,
 }
DESCRIPTIONS = {
"t": """**tea, thé, té**, etc
from Min Nan //tê//, mostly via Dutch and English""",
"ot": """with an additional morpheme:
• Polish **herbata**, Lithuanian **arbata** < Latin //herba thea//
• Malagasy **dite** < French //du thé//""",
"c": """**chá, chāy, shāy**, etc
from Mandarin //chá///Cantonese //chàh//, via Persian or Portuguese""",
"oc": """with an additional morpheme:
• Wolof **àttaaya** < Arabic aš-šhāy""",
"o": """from another origin:
• Japanese/Korean **ta**, Vietname **trà**, Bhutanese **ja** < Middle Chinese
• Burmese **lakhpak** ("arm leaf")
• Quechua **q’uñi yaku** ("warm water")
• Shona **putugadzike**
• Guarani **ñanary**"""
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

colormap = { c: df.category[c] if df.category[c] in PALETTE else "o" for c in df.index }
generate_datamap("etymtea", colormap, palette=PALETTE, patterns=PATTERNS, codifier=partial(codify_countries, dependencies=False))

chart = Image.open("temp/etymtea.png")
legend = generate_legend(
  [PALETTE[c] for c in DESCRIPTIONS],
  [DESCRIPTIONS.get(c,c) for c in DESCRIPTIONS],
  (40,...), partial(sans, 16), header="Most commmon word for tea".upper())
chart = chart.place(legend, align=(0,1), padding=100)

title = Image.from_column([
Image.from_text("TEA VERSUS CHAI", sans(72, bold=True)),
Image.from_text("the word for tea around the world", sans(36, italics=True))],
bg="white")

img = Image.from_column([title, chart], bg="white", padding=5)
img.place(Image.from_text("/u/Udzu", sans(16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/etymtea.png")

