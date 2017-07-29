import sys
sys.path.append('..')
from charts import *
from records import *
from scipy import ndimage
import seaborn as sns

MAP = "maps/Europe.png"
BACKGROUND = 'Sea'
IGNORE = ('Gibraltar', 'Faroe Islands', 'Jersey', 'Guernsey')
IGNORECOLOR = 'grey'
PLOTS = ('UK',)

mapnames = RecordCSV.load_file(name_csv_path(MAP))
names = [d['name'] for d in mapnames if d['name'] not in IGNORE and d['name'] != BACKGROUND]
bgcolor = first_or_none([tuple(d['color']) for d in mapnames if d['name'] == BACKGROUND])
palette = [tuple(int(x*255) for x in c) for c in sns.color_palette("hls", len(names))]
colorfn = lambda n: None if n == BACKGROUND else IGNORECOLOR if n in IGNORE else palette[names.index(n)]
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
    return base.place(borders)

