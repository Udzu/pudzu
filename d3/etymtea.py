from pudzu.charts import *
from generate import *


FONT = sans
DEFAULT = VegaPalette10.GREEN
PALETTE = { "t": VegaPalette10.BLUE, "c": VegaPalette10.GREEN, "ot": VegaPalette10.LIGHTBLUE, "oc": VegaPalette10.LIGHTGREEN, "o": VegaPalette10.RED }

df = pd.read_csv("datasets/etymtea.csv").set_index("country")

assert set(df.index) < set(load_name_csv("../dataviz/maps/World.png").name), f'Unrecognised countris: {set(df.index) - set(load_name_csv("../dataviz/maps/World.png").name)}'

# TODO: stripes
colormap = { c: PALETTE.get(r.category, VegaPalette10.RED) for c,r in df.iterrows() }
generate_datamap("etymtea", colormap, codifier=partial(codify_countries, dependencies=False))
