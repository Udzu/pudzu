import sys
sys.path.append('..')
from charts import *
from records import *
from scipy import ndimage
import seaborn as sns
import imageio
import os

# TODO: better palette, align title better, convert to GIF

MAP = "maps/Europe.png"
BACKGROUND = 'Sea'
MERGE = { 'Gibraltar': 'UK', 'Jersey': 'UK', 'Guernsey': 'UK', 'Faroe Islands': 'Denmark' }
IGNORECOLOR = 'grey'

mapnames = RecordCSV.load_file(name_csv_path(MAP))
names = [d['name'] for d in mapnames if d['name'] not in MERGE and d['name'] != BACKGROUND]
bgcolor = first_or_none([tuple(d['color']) for d in mapnames if d['name'] == BACKGROUND])
palette = [tuple(int(x*255) for x in c) for c in sns.color_palette("hls", len(names))]
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

def country_borders(country):
    cmask = mask_by_color(maparray, palette[names.index(country)])
    edtmask = cmask | mask_by_color(maparray, bgcolor) | mask_by_color(maparray, IGNORECOLOR)
    _, (indx,indy) = ndimage.distance_transform_edt(edtmask, return_indices=True)
    edtvals = maparray[indx,indy]
    for i in range(edtvals.shape[-1]): edtvals[...,i] *= cmask
    return Image.fromarray(edtvals)
    
def one_country(country):
    borders = country_borders(country)
    bordercolors = [c for _,c in borders.getcolors()]
    base = map.copy()
    for _,c in base.getcolors():
        if c[:3] == bgcolor[:3]: continue
        elif c not in bordercolors: base = base.replace_color(c, IGNORECOLOR)
    base.place(borders, copy=False)
    title = Image.from_row([Image.from_text("The near country to:", arial(60, bold=True), "black", "white", padding=20),
                            Image.from_text(country, arial(60, bold=True), "red", "white")], bg="white")
    footer = Image.from_text("Blank map from Wikipedia. Dependencies counted under parent state. Calculations based on Euclidean distance and low resolution map, so not 100% accurate.", arial(16), "black", "white", padding=10)
    chart = Image.from_column([title, base, footer], bg="white", xalign=0)
    chart.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
    return chart

def make_gif(countries, basename, duration):
    pngs = []
    for i,c in tqdm.tqdm(list(enumerate(countries))):
        png = "{}_{:02d}.png".format(basename, i)
        one_country(c).save(png)
        pngs.append(png)
    imageio.mimsave("{}.gif".format(basename), [imageio.imread(f) for f in pngs], duration=duration)
    for p in pngs: os.remove(p)

make_gif(('UK', 'France', 'Spain', 'Italy', 'Germany', 'Poland'), "neighbours", 4)
