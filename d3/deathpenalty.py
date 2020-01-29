from pudzu.charts import *
from generate import *

# Source: Amnesty + (note Gambia, DR Congo, etc)
# https://www.amnesty.org/download/Documents/ACT5098702019ENGLISH.PDF
# only 20 in 2018 and only 36 in the last 10 years

df = pd.read_csv("datasets/deathpenalty.csv").set_index("country")
assert set(df.index) < set(atlas.index), f'Unrecognised countries: {set(df.index) - set(atlas.index)}'

PALETTE = {
    "all": "#045a8d", "ordinary": "#2b8cbe", "moratorium": "#74a9cf",
    "hanging": VegaPalette10.RED, "shooting": VegaPalette10.ORANGE, "injection": VegaPalette10.GREEN, "stoning": VegaPalette10.BROWN,
    "decapitation": VegaPalette10.PURPLE, "electrocution": VegaPalette10.PINK, "gas": VegaPalette10.LIGHTGREEN,
    "other": VegaPalette10.GREY }

PATTERNS = ""

for p in df.position:
    if isinstance(p, str) and p not in PALETTE:
        ps = p.split("|")
        if all(p in PALETTE for p in ps):
            rects = [f'<rect x="{i*6}" y="0" width="{6}" height="{6*len(ps)}" style="fill:{PALETTE[p].to_hex()}"/>' for i,p in enumerate(ps)]
            PATTERNS += f'''<defs>
  <pattern id="{''.join(ps)}" width="{6*len(ps)}" height="{6*len(ps)}" patternTransform="rotate(45 0 0)" patternUnits="userSpaceOnUse">
    {'  '.join(rects)}
  </pattern>
</dev>
'''
            PALETTE[p] = f'url(#{"".join(ps)})'
        else: print(ps)

colormap = { c: df.position[c] if df.position[c] in PALETTE else "other" for c in df.index }
generate_datamap("deathpenalty", colormap, palette=PALETTE, patterns=PATTERNS)

# chart = Image.open("temp/jewishleaders.png")
# legend = generate_legend(
  # [PairedClass12.BLUE,PairedClass12.GREEN,PairedClass12.LIGHTGREEN],
  # ["Head of state or government (president, PM, etc)",
  # "Colonial or national governor",
  # "Acting governor"], 40, partial(arial, 16), header="Countries that have had a Jewish or half-Jewish:")
# chart = chart.place(legend, align=(0,1), padding=100)

# title = Image.from_markup("**Countries that have had a national leader of Jewish origin**".upper(), partial(arial, 60))
# img = Image.from_column([title, chart], bg="white", padding=5)
# img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
# img.save("output/politics_jewishleaders.png")
