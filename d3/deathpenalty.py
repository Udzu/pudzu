from pudzu.charts import *
from generate import *

# Source: Amnesty + Gambia

df = pd.read_csv("datasets/deathpenalty.csv").set_index("country")

assert set(df.index) < set(atlas.index), f'Unrecognised countris: {set(df.index) - set(atlas.index)}'

# TODO: fill patterns
PALETTE = { "all": "#045a8d", "ordinary": "#2b8cbe", "moratorium": "#74a9cf" }

colormap = { c: PALETTE.get(df.position[c], VegaPalette10.RED) for c in df.index }
generate_datamap("deathpenalty", colormap, default_fill=VegaPalette10.ORANGE)

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
