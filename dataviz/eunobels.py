import sys
import seaborn as sns

sys.path.append('..')
from charts import *
from bamboo import *

# ------------------------
# Nobel prizes by US state
# ------------------------

SIZE = 50

tiles = pd.read_csv("maps/europe_tiles.csv", names=range(15)).as_matrix()
generate_tile_map(tiles, "cache/europe_tiles_map.png", SIZE)

countries = pd.read_csv("datasets/countries.csv").split_columns(('nationality', 'tld', 'country'), "|").split_rows('tld').update_columns(tld=lambda v: v[1:]).set_index('tld')

def colorfn(c):
    if not isinstance(c, str): return None
    p = 200 - countries['population'][c] // 1000000
    return RGBA(p,p,p,255)
    
def labelfn(c):
    if not isinstance(c, str): return None
    return Image.from_text(c, arial(16, bold=True), fg="black", padding=1)
    
chart = map_chart("cache/europe_tiles_map.png", colorfn, labelfn)
