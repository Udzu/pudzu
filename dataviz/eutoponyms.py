from pudzu.charts import *
from pudzu.bamboo import *
import seaborn as sns

# a selection of words dervied from European toponyms (excluding wines and cheeses)

# dataset: a hacky mess but it'll do

countries = { 
    'Spain': 'spaniel',
    'Bulgaria': 'bugger', 
    'Cyprus': 'copper', 
    'Croatia': 'cravat',
    'Turkey': '\n\nturkey\nturquoise\n',
    'Sweden': 'suede\nswede',
    'Denmark': 'Danish',
    # 'Poland': 'polonaise',
    'Italy': 'italics',
    'Malta': 'maltese'
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
    'dollar': (635, 740, True),
    'bohemian': (680, 760, True),
# France
    'denim': (430, 965),
    'bayonet': (280, 955),
    'limousine': (350, 900),
    'vaudeville': (325, 780),
    'cognac': (315, 890, True),
    'alsatian': (495, 815),
# Germany   
    'frankfurter': (530, 760),
    'hamburger': (555, 635),
    'neanderthal': (505, 715, True),
    'cologne': (503,728),
    'spruce': (620, 670),
# Greece
    'lesbian': (990, 1075),
    'academia\nattic': (920, 1120),
    'marathon': (932, 1118, True),
    'spartan': (890, 1155),
    'magnet': (885, 1080, True),
# Hungary
    'coach': (745, 830),
# Iceland
    'geyser': (125,185),
# Ireland
    'limerick': (180, 620),
    'beyond the pale': (225, 615, True),
# Italy
    'magenta': (525, 905),
    'jeans': (530, 940),
    'sardines\nsardonic': (535, 1080),
    'tarantula': (755, 1065),
    'volcano': (692, 1142),
    'bolognese': (580, 930),
    'romantic': (622, 1027),
# Jersey
    'jersey': (292, 762),
# Netherlands
    'hollandaise': (450, 680, True),
# Norway
#    'maelstrom': (615, 130),
# Poland
    'pomeranian': (650, 635),
# Spain
    'mayonnaise': (405, 1090),
# Switzerland
    'Jurassic': (490, 840),
    'alpine': (485, 895),
# Turkey
    'parchment': (1020, 1075, True),
    'meander': (1035, 1085),
    'angora': (1150, 995),
    'trojan horse': (990, 1040, True),
# UK
    'badminton': (305, 685, True),
    'rugby': (325, 655, True),
    'cardigan': (260, 660, True),
    'wellies': (290, 700),
    'derby': (325, 625, True),
    # 'Cambrian': (285, 650, True),
    'sandwich': (370, 705),
    'paisley': (285, 530),
    'tweed': (315, 550),
    'scotch': (285, 485, True),
# Ukraine
    'balaclava': (1125, 845)
}

city_countries = {
    'Austria', 'Belgium', 'Czech Republic', 'France', 'Germany', 'Greece',
    'Hungary', 'Iceland', 'Ireland', 'Italy', 'Jersey',
    'Netherlands', 'Poland', # 'Norway',
    'Switzerland', 'UK', 'Ukraine'
}

# visualisation

blues = tmap(RGBA, sns.color_palette("Blues", 6))
reds = tmap(RGBA, sns.color_palette("Reds", 6))

COUNTRY_BG = blues[3]
COUNTRY_LABEL = blues[-1]
CITY_LABEL = reds[-1]
CITY_BG = RGBA(red=251, green=129, blue=129, alpha=255)

def country_color(c):
    if c in ['Sea', 'Borders']: return "white"
    elif c in df.index: return COUNTRY_BG
    elif c in city_countries: return CITY_BG
    else: return "#AAAAAA"

def country_label(c):
    if c not in df.index: return None
    else: return Image.from_text(df.toponym[c], arial(16, bold=True, italics=(c == 'Italy')), COUNTRY_LABEL, align="center")

df = pd.DataFrame([{ 'country': k, 'toponym': v} for k,v in countries.items() ]).set_index('country')
map = map_chart("maps/Europe.png", country_color, country_label)

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
        if len(up) > 0:
            img = img.pin(city_label(l, True), (x, y+5), (0.5, 1))
        else:
            img = img.pin(city_label(l, False), (x, y-5), (0.5, 0))
    return img
    
map = add_cities(map, cities)

title = Image.from_column([
Image.from_text("words that derive from European place names", arial(48, bold=True)),
Image.from_text("an incomplete list that excludes cheese and wines", arial(36, italics=True))],
bg="white")

img = Image.from_column([title, map], bg="white")
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)

img.save("output/eutoponyms.png")
