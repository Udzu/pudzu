from pudzu.charts import *
from pudzu.sandbox.bamboo import *
import seaborn as sns

# a selection of words dervied from European toponyms (excluding wines and cheeses)

# dataset: a hacky mess but it'll do

countries = { 
    'Spain': 'spaniel',
    'Bulgaria': 'bugger', 
    'Cyprus': 'copper', 
    'Croatia': 'cravat',
    'Turkey': 'turkey\nturquoise\nottoman',
    'Sweden': 'suede\nswede',
    'Denmark': 'Danish',
    'Poland': 'polonium',
    'Italy': 'italics\n ',
    'Malta': 'maltese',
    'Iran': 'peach',
    'France': 'francium\ngallium',
    'Germany': 'germanium\n ',
    'Russia': 'ruthenium\n \n \n \n ',
}

cities = {
# Austria
    'wiener': (705, 805),
# Belgium
    'spa': (470, 745),
    'duffel bag': (445, 715),
# Croatia
    'dalmatian': (705, 950),
# Czechia
    'pilsner': (640, 760),
    'Budweiser    ': (660, 790),
    'dollar': (635, 740, True),
    'bohemian': (680, 760, True),
# Denmark
    'hafnium': (600, 568),
# Finland
    'Nokia': (772, 350),
# France
    'denim': (430, 965),
    'bayonet': (280, 955, True),
    'limousine': (350, 900),
    'vaudeville': (325, 780),
    'lutetium': (385, 800),
    'cognac': (315, 890, True),
    'armagnac': (330, 955),
    'tulle': (340, 945, True),
    'alsatian': (495, 815),
    'burgundy': (435, 825),
    'frankly': (470, 773),
    'chartreuse': (470, 925),
# Germany   
    'rottweiler': (525, 815, True),
    'rhenium': (545, 830),
    'frankfurter': (530, 760),
    'hamburger': (555, 635),
    'neanderthal': (507, 715, True),
    'cologne': (505,728),
# Greece
    'lesbian': (990, 1075),
    'academia\nattic': (920, 1120, True),
    'marathon': (932, 1118),
    '       currant': (912, 1144),
    'laconic\nspartan': (890, 1158),
    'Olympics': (870, 1140, True),
    'magnet\nmagnesium\nmanganese': (885, 1075, True),
    'quince': (960, 1215),
# Hungary
    'coach': (745, 830),
# Iceland
    'geyser': (125,185),
# Ireland
    'limerick': (180, 620),
# Italy
    'magenta': (525, 905),
    'jeans': (530, 940),
    'sardines\nsardonic': (535, 1080),
    'tarantula': (755, 1065),
    'volcano': (692, 1142),
    'bolognese': (580, 930),
    'romantic\npalace\ncapitol': (622, 1027),
    'cantaloupe': (626, 1015, True),
    'sienna': (585, 975, True),
# Jersey
    'jersey': (292, 762),
# Morocco:
    'tangerine': (120, 1200, True),
    'fez': (130, 1235, True),
# Netherlands
    'hollandaise': (450, 680, True),
# Norway
    'scandium': (595, 385),
# Poland
    'pomeranian': (650, 635),
# Russia
    'muscovite': (1050, 470),
    'spruce': (780, 580),
# Spain
    'cordovan': (150, 1125, True),
# Sweden
    'holmium': (700, 430),
    'erbium\nterbium\nytterbium\nyttrium': (705, 425, True),
# Switzerland
    'alpine': (485, 893),
# Turkey
    'parchment': (1020, 1075, True),
    'meander': (1035, 1085),
    'mausoleum': (1035, 1115),
    'jet black': (1120, 1135),
    'angora': (1150, 995),
    'trojan horse': (990, 1040, True),
    'byzantine': (1045, 990, True),
    'solecism': (1235, 1085, True),
# UK
    'badminton': (305, 685, True),
    'bedlam': (352, 695, True),
    'rugby': (325, 655, True),
    'cardigan': (260, 660, True),
    'wellies': (290, 700),
    'derby': (325, 625, True),
    'sandwich': (370, 705),
    'paisley': (285, 530, True),
    'strontium': (285, 545),
    'tweed': (315, 550, True),
    'scotch': (285, 485, True),
# Ukraine
    'balaclava': (1125, 845),
# Lebanon
    'Bible      ': (1282, 1160, True),
# Israel
    'armageddon': (1285, 1212, True),
# Iraq
    'muslin': (1450, 1020),
# Armenia
    'caucasian': (1430, 855, True),
# Syria
    '      damask\n      damson': (1305, 1183, True),
# Tunisia
    'afro': (565, 1200, True),
# Palestine
    'samaritan': (1288, 1222),
}

city_countries = {
    'Austria', 'Belgium', 'Czech Republic', 'France', 'Germany', 'Greece',
    'Hungary', 'Iceland', 'Ireland', 'Italy', 'Jersey',
    'Netherlands', 'Poland', 'Luxembourg', 'Norway',
    'Switzerland', 'UK', 'Ukraine', 'Russia', 'Finland',
    'Morocco', 'Lebanon', 'Israel', 'Iraq',
    'Armenia', 'Georgia', 'Azerbaijan', 'Syria', 'Tunisia', 'Palestine',
}

# visualisation

blues = tmap(RGBA, sns.color_palette("Blues", 6))
reds = tmap(RGBA, sns.color_palette("Reds", 6))

COUNTRY_BG = blues[3]
COUNTRY_LABEL = blues[-1]
CITY_LABEL = reds[-1]
CITY_BG = RGBA(red=251, green=129, blue=129, alpha=255)

BIG = True

def country_color(c):
    if c in ['Sea', 'Borders']: return "white"
    elif c in df.index: return COUNTRY_BG
    elif c in city_countries: return CITY_BG
    else: return "#AAAAAA"

def country_label(c):
    if c not in df.index: return None
    else: return Image.from_text(df.toponym[c], arial(16, bold=True, italics=(c == 'Italy')), COUNTRY_LABEL, align="center")

df = pd.DataFrame([{ 'country': k, 'toponym': v} for k,v in countries.items() ]).set_index('country')
map = map_chart(f"maps/Europe{'2'*BIG}.png", country_color, country_label)

def circle(r, bg):
    img = Image.new("RGBA", (2*r, 2*r))
    draw = ImageDraw.Draw(img)
    draw.ellipse((0, 0, 2*r-1, 2*r-1), fill=bg)
    return img
    
def city_label(label, above=False): # TODO alignment
    dot = circle(20, CITY_LABEL).resize_fixed_aspect(scale=0.25)
    text = Image.from_text(label, arial(16, bold=True), CITY_LABEL, align="center", padding=(0,0,0,4))
    return Image.from_column([text, dot] if above else [dot, text], bg=0)
    
def add_cities(img, cities):
    img = img.copy()
    for l, (x,y, *up) in cities.items():
        if BIG:
            x -= 5
        if not ((0 <= x <= img.width) and (0 <= y <= img.height)):
            print(f"Skipping {l}")
            continue
        if len(up) > 0:
            img = img.pin(city_label(l, True), (x, y+5), (0.5, 1))
        else:
            img = img.pin(city_label(l, False), (x, y-5), (0.5, 0))
    return img
    
map = add_cities(map, cities)
legend = generate_legend([COUNTRY_BG, Rectangle(40, CITY_BG).place(circle(20, CITY_LABEL).resize_fixed_aspect(scale=0.25))],
                         ["word(s) named after a country", "word(s) named after places inside a country"], box_sizes=40, font_family=partial(sans, 18))
chart = map.place(legend, align=(1,0), padding=10)


def num(l): return sum(1 for x in l for y in x.split("\n") if y.strip())
N = num(cities) + num(countries.values())

title = Image.from_column([
Image.from_text(f"{N} English words that derive from place names".upper(), arial(48, bold=True)),
Image.from_text("an incomplete list that excludes cheese and wines", arial(36, italics=True))],
bg="white")

img = Image.from_column([title, chart], bg="white")
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)

img.save("output/eutoponyms.png")
