from pudzu.charts import *

FONT = arial
DEFAULT = VegaPalette10.GREEN
PALETTE = { "p": VegaPalette10.ORANGE, "o": VegaPalette10.BROWN, "?": "#aaaaaa", "a": DEFAULT }

df = pd.read_csv("datasets/etymananas.csv").set_index("country").fillna("")

countries = set(df.index)

def colorfn(c):
    if c in ['Sea', 'Borders']: return "white"
    elif c not in df.index: return DEFAULT
    countries.remove(c)
    cols = [PALETTE[t] for t in df.category[c]]
    if len(cols) == 1: return cols[0]
    else: return Stripe(20, *cols)

world_map = map_chart("maps/World.png", colorfn)

world_map.save("output/etymananas.png")

print("\n".join(countries))
