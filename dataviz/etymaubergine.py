from pudzu.charts import *
from pudzu.sandbox.bamboo import *
from PIL import ImageEnhance

df = pd.read_csv("datasets/etymaubergine.csv").set_index("language").fillna("a")
FONT = sans
UFONT = partial(font, "fonts/arialu")
LFONT = lambda l: FONT if l not in ["Georgian", "Armenian", "Arabic", "Hebrew", "Persian"] else UFONT

CATEGORIES = ["a", "e", "c", "s", "?" ]
PALETTE = [VegaPalette10.PURPLE, VegaPalette10.ORANGE, VegaPalette10.BLUE, VegaPalette10.GREEN, VegaPalette10.BROWN.brighten(0.05) ]

LEFT = [
    "https://www.compo-expert.com/sites/default/files/styles/title_image_xl_/public/2020-02/vegetables-aubergines-title.jpg",
    "https://idsb.tmgrup.com.tr/ly/uploads/images/2020/03/20/thumbs/1200x600/26333.jpg",
    "https://www.thespruceeats.com/thmb/6m4sAEpiAIV5lOGPUYqoQm69Wrk=/1500x1015/filters:fill(auto,1)/moussaka-with-eggplant-1705452-Hero-5b79985446e0fb004f78ac34.jpg",
    "https://716f24d81edeb11608aa-99aa5ccfecf745e7cf976b37d172ce54.ssl.cf1.rackcdn.com/georgian-rolls-nigvziani-badrijani-1826212l1.jpg",
    "http://gastropedia.ro/wp-content/uploads/2018/07/Salata-de-vinete-cu-usturoi_edited.jpg",
]

RIGHT = [

    "https://i.ytimg.com/vi/uIASVBSpsCo/maxresdefault.jpg",
    "https://www.31daily.com/wp-content/uploads/2012/08/md_ratatouille.jpg",
    "https://img.taste.com.au/rTAxfC1d/taste/2019/05/cheesy-stuffed-eggplant-parmigiana-149313-1.jpg",
    "https://s23991.pcdn.co/wp-content/uploads/2011/09/catalan-bread-salad-escalivada-recipe-fp.jpg",
    "http://nibbledish.com/wp-content/legacy-recipe-images/6008c9d82c99c9655b599aca1b6e1dc8.jpg",
]

DESCRIPTIONS = [
"""from **Proto-Dravidian** //*waẒ-Vt-//, via **Sanskrit** //vātiga-gama// (folk loan for “plant that cures flatulence”), via **Persian** بادنجان //bâdenjân// and **Arabic** باذنجان //bādinjān//.
- Italian //melanazana// is by influence of //mela// ("apple").
- French //aubergine// is from **Catalan** //albergínia//, with **Arabic** ال //al-// ("the").""",
"""from the word for **egg**:
- Finnish: muna (“egg”) + koiso (“nightshade”)
- Slovene: jájce ("egg")
- Welsh: wy ("egg") + llysiau ("vegetables")
- Icelandic: egg (“egg”) + aldin (“fruit”)
- Irish: ubh (“egg”) +‎ toradh (“fruit”)""",
"""from its **color**:
- Romanian: from vânăt ("dark blue"), originally //pătlăgea vânătă//
- Macedonian: from модар ("blue") + патлиџан
- Serbian: from плави ("blue") + парадајз""",
"""from another **plant**:
- Kazakh: from Persian کدو //kadu// ("squash")
- Czech: from Latin //lolium// ("ryegrass")""",
"""from its **shape**:
- Hebrew: from Syrian Arabic حيصل //ḥayṣal// from حوصل //ḥawṣal// ("pocket, pouch")""",
]
FOOTER = None
 
def colorfn(c):
    if c in ['Sea', 'Language Borders']: return "white"
    elif c in ['Country Borders']: return "#AAAAAA"
    elif c not in df.index: return "grey"
    elif "|" in df.group.get(c):
        colors = [PALETTE[CATEGORIES.index(i)] for i in df.group[c].split("|")]
        return Stripe(20, *colors)
    else: return PALETTE[CATEGORIES.index(df.group.get(c))]
    
def labelfn(c, w, h):
    # Unicode workarounds generated with https://vincent7128.github.io/text-image/
    if c not in df.index: return None
    label = df.word[c].replace("\\n", "\n")
    filename = "text/aubergine_{}.png".format(c.lower())
    if os.path.exists(filename):
        img = Image.open(filename)
    else:
        img = Image.from_text_bounded(label, (w, h), 24, papply(LFONT(c), bold=True), align="center", padding=(0,0,0,2))
    return img
    
map = map_chart("maps/Eurolang2.png", colorfn, labelfn)
legend = generate_legend(PALETTE[:len(CATEGORIES)], DESCRIPTIONS, box_sizes=(40,...), footer=FOOTER, font_family=partial(FONT, 16), max_width=650)
chart = map.place(legend, align=(1,0), padding=10)

title = Image.from_column([
Image.from_text("THE WORD FOR 'EGGPLANT' IN DIFFERENT LANGUAGES", FONT(48, bold=True)),
#Image.from_text("most common terms for the motor fuel, with etymologies", FONT(36)),
],
bg="white")

img = Image.from_column([title, chart], bg="white", padding=2)
img = ImageEnhance.Color(img).enhance(0.7)

def sidebar(images):
    images = [Image.from_url_with_cache(image).crop_to_aspect(1.8).resize_fixed_aspect(width=200) for image in images]
    return Image.from_column(images).resize_fixed_aspect(height = img.height)

img2 = Image.from_row([sidebar(LEFT), img, sidebar(RIGHT)])

img2.place(Image.from_text("/u/Udzu", FONT(16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)

img2.save("output/etymaubergine.png")

