import sys
sys.path.append('..')
from charts import *
from scipy import ndimage
import seaborn as sns
import tqdm

MAP = "maps/Europe.png"
BACKGROUND = 'Sea'
MERGE = { 'Gibraltar': 'UK', 'Jersey': 'UK', 'Guernsey': 'UK', 'Faroe Islands': 'Denmark' }

mapnames = load_name_csv(MAP)
names = [d['name'] for _,d in mapnames.iterrows() if d['name'] not in MERGE and d['name'] != BACKGROUND]
bgcolor = mapnames[mapnames['name']==BACKGROUND].color.loc[0]
# palette = ImageColor.from_floats(sns.color_palette("hls", len(names) * 2)[len(names):])
palette = ImageColor.from_floats(sns.cubehelix_palette(len(names) * 2, start=0.2, rot=-0.75))
palette = list(riffle_shuffle(palette, 4))
colorfn = lambda n: None if n == BACKGROUND else palette[names.index(MERGE[n])] if n in MERGE else palette[names.index(n)]
map = map_chart(MAP, colorfn).convert("RGBA")
maparray = np.array(map)

def mask_by_color(nparray, color):
    color = ImageColor.getrgba(color)
    channels = [nparray[...,i] for i in range(nparray.shape[-1])]
    mask = np.ones(nparray.shape[:-1], dtype=bool)
    for c,channel in zip(color, channels):
        mask = mask & (channel == c)
    return mask

def one_country(country):
    cmask = mask_by_color(maparray, palette[names.index(country)])
    edtmask = cmask | mask_by_color(maparray, bgcolor)
    _, (indx,indy) = ndimage.distance_transform_edt(edtmask, return_indices=True)
    edtvals = maparray[indx,indy]
    for i in range(edtvals.shape[-1]): edtvals[...,i] *= cmask
    return Image.fromarray(edtvals)
    
def all_countries():
    base = map.copy()
    for c in tqdm.tqdm(names):
        base.place(one_country(c), copy=False)
    return base
    
all = all_countries()

maps = Image.from_array([[Image.from_text("Original map".upper(), arial(60, bold=True), "black", "white"),
                          Image.from_text("Closest country".upper(), arial(60, bold=True), "black", "white")],
                         [map, all]], bg="white", padding=10)
footer = Image.from_text("Blank map from Wikipedia. Dependencies counted under parent state. Calculations based on Euclidean distance and low resolution map, so not 100% accurate. Not for use in pub quizzes or planning escape routes.", arial(24), "black", "white", padding=10)
chart = Image.from_column([maps, footer], bg="white")
chart.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, copy=False)
chart.save("output/neighbours.png")

