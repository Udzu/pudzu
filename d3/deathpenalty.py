from pudzu.charts import *
from generate import *

# Source: Amnesty + (note Gambia, DR Congo, etc)
# https://www.amnesty.org/download/Documents/ACT5098702019ENGLISH.PDF
# only 20 in 2018 and only 36 in the last 10 years

df = pd.read_csv("datasets/deathpenalty.csv").set_index("country")
assert set(df.index) < set(atlas.index), f'Unrecognised countries: {set(df.index) - set(atlas.index)}'

PALETTE = {
    "all": "#c0c0c0", "ordinary": "#a0a0a0", "moratorium": "#808080", # 5-class PuBu
    "all": "#045a8d", "ordinary": "#2b8cbe", "moratorium": "#74a9cf",
    "hanging": VegaPalette10.RED, "shooting": VegaPalette10.ORANGE, "injection": VegaPalette10.BROWN, "stoning": VegaPalette10.PURPLE,
    "decapitation": VegaPalette10.PINK, "electrocution": VegaPalette10.GREEN, "gas": VegaPalette10.LIGHTGREEN,
    "other": VegaPalette10.GREY }

PATTERNS = ""
WIDTH = 3

for p in df.position:
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
        else: print(ps)

colormap = { c: df.position[c] if df.position[c] in PALETTE else "other" for c in df.index }
generate_datamap("deathpenalty", colormap, palette=PALETTE, patterns=PATTERNS)

chart = Image.open("temp/deathpenalty.png")
counts = df.position.str.split("|").explode().value_counts()

legend1 = generate_legend(
  [Rectangle((40,40),PALETTE[x]).place(Image.from_text(str(counts[x]), sans(14), "white")) for x in ["all", "ordinary", "moratorium"]],
  ["Capital punishment abolished for all crimes.", 
   "Abolished for all but exceptional crimes such as treason, and no exeuctions in the last 20 years.",
   "Abolished in practice: policy is not to execute, and no executions in the last 20 years."],
   40, partial(sans, 16), header="Abolitionist countries", max_width=400, border=False,
   footer="Of the 56 retentionist countries, just 20 carried out executions in 2018, and only 36 the last 10 years.")
   
legend2 = generate_legend(
  [Rectangle((40,40),PALETTE[x]).place(Image.from_text(str(counts[x]), sans(14), "white")) for x in ["hanging", "shooting", "stoning", "injection", "decapitation", "electrocution", "gas"]],
   ["Hanging",
   "Shooting (single shot or firing squad)",
   "Stoning",
   "Lethal injection",
   "Beheading",
   "Electrocution",
   "Gas inhalation"],
   40, partial(sans, 16), header="Execution methods", max_width=400, border=False)
   
legend = Image.from_column([legend1, legend2], xalign=0).pad(1, "black")

chart = chart.place(legend, align=(0,1), padding=50)

title = Image.from_markup("**Death penalty methods around the world**".upper(), partial(sans, 80))
# TODO: footer with source
img = Image.from_column([title, chart], bg="white", padding=5)
img.place(Image.from_text("/u/Udzu", sans(16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/deathpenalty.png")
