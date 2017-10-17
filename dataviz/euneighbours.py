import sys
sys.path.append('..')
from charts import *
from scipy import ndimage
import seaborn as sns
import tqdm

MAP = "maps/Europe.png"
MERGE = { 'Gibraltar': 'UK', 'Jersey': 'UK', 'Guernsey': 'UK', 'Faroe Islands': 'Denmark' }
COLOR = { 'Sea': '#E0E0FF', 'Borders': 'white', 'Land': 'white' }
PALETTE_ARGS = { 'start': 0.2, 'rot': -0.75, 'hue': 0.9, 'light': 0.85 }
#PALETTE_ARGS = { 'start': 0.7, 'rot': -1.0, 'hue': 0.9, 'light': 0.85 }

mapnames = load_name_csv(MAP)
uncolored = [d['name'] for _,d in mapnames.iterrows() if d['name'] not in MERGE and d['name'] not in COLOR]
palette = ImageColor.from_floats(sns.cubehelix_palette(len(uncolored), **PALETTE_ARGS))
palette = riffle_shuffle(palette, 6)
palette = { c : p for c,p in zip(uncolored, palette) }
palette['Estonia'], palette['Belarus'] = palette['Belarus'], palette['Estonia']

def colorfn(c):
    if c in COLOR: return COLOR[c]
    elif c in MERGE: return colorfn(MERGE[c])
    else: return palette[c]

def mask_by_color(nparray, color):
    color = ImageColor.getrgba(color)
    channels = [nparray[...,i] for i in range(nparray.shape[-1])]
    mask = np.ones(nparray.shape[:-1], dtype=bool)
    for c,channel in zip(color, channels):
        mask = mask & (channel == c)
    return mask

def one_country(maparray, country, background):
    cmask = mask_by_color(maparray, colorfn(country))
    edtmask = cmask
    for c in background:
        edtmask = edtmask | mask_by_color(maparray, colorfn(c))
    _, (indx,indy) = ndimage.distance_transform_edt(edtmask, return_indices=True)
    edtvals = maparray[indx,indy]
    for i in range(edtvals.shape[-1]): edtvals[...,i] *= cmask
    return Image.fromarray(edtvals)
    
def all_countries(basemap, ignore, dontshow):
    background = ignore | { c for c,d in MERGE.items() if d in ignore }
    foreground = [d['name'] for _,d in mapnames.iterrows() if d['name'] not in background and d['name'] not in dontshow]
    base = basemap.copy()
    maparray = np.array(basemap)
    for c in tqdm.tqdm(foreground):
        base.place(one_country(maparray, c, background), copy=False)
    return base

def map_title(text):
    return Image.from_text(text.upper(), arial(60, bold=True), "black", "white")
    
map = map_chart(MAP, colorfn).convert("RGBA")
closest = all_countries(map, { 'Borders', 'Sea' }, { })
closest_sea = all_countries(map, { 'Borders' }, { 'Sea' })

countries = {d['name'] for _,d in mapnames.iterrows() if d['name'] not in { 'Borders', 'Sea' }}
closest_to_sea = all_countries(map, { 'Borders' }, countries)
for c in tqdm.tqdm(countries):
    cmask = map.select_color(colorfn(c))
    closest_to_sea.place(Image.new("RGBA", map.size, COLOR['Land']), mask=cmask, copy=False)

maps = Image.from_array([[map_title("Map of Europe"), map_title("Closest country")],
                         [map, closest],
                         [map_title("Closest country or sea"), map_title("Closest country at sea")],
                         [closest_sea, closest_to_sea]],
         bg="white", padding=10)
footer = Image.from_text("*Blank map from Wikipedia. Dependencies counted under parent state. Calculations based on Euclidean distance and low resolution map, so not 100% accurate. Not for use in pub quizzes or planning actual escape routes.", arial(24), "black", "white", padding=10)
header = Image.from_text("Where to run: the closest country to places in Europe*", arial(96, bold=True, italics=True), "black", "white", padding=10)
chart = Image.from_column([header, maps, footer], bg="white")
chart.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, copy=False)
chart.save("output/euneighbours.png")

