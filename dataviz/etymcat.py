from pudzu.charts import *
from pudzu.sandbox.bamboo import *
from PIL import ImageEnhance

df = pd.read_csv("datasets/etymcat.csv").set_index("language").fillna("o")
FONT = sans

CATEGORIES = ["c", "m", "k" ]
PALETTE = [VegaPalette10.BLUE, VegaPalette10.RED, VegaPalette10.GREEN, "#AAAAAA" ]

DESCRIPTIONS = [ """probably of Afro-Asiatic origin, via Latin //cattus//, Proto-Germanic *//kattuz// and Proto-Slavic *//kotъ//""",
                 """from Proto-Slavic *//maca// ("pussycat"), probably onomatopoeic ("animal that meows")""",
                 """from the sound used to call a cat (pisică from //pis,// kissa from Swedish //kiss//)""" ]
FOOTER = None
 
def colorfn(c):
    if c in ['Sea', 'Language Borders']: return "white"
    elif c in ['Country Borders']: return "#AAAAAA"
    elif c not in df.index: return "grey"
    else: return PALETTE[CATEGORIES.index(df.group.get(c))]
    
def labelfn(c, w, h):
    if c not in df.index: return None
    label = df.word[c].replace("\\n", "\n")
    filename = "text/cat_{}.png".format(c.lower())
    if os.path.exists(filename):
        img = Image.open(filename)
    else:
        img = Image.from_text_bounded(label, (w, h), 24, papply(FONT, bold=True), align="center", padding=(0,0,0,2))
    return img
    
map = map_chart("maps/Eurolang.png", colorfn, labelfn)
legend = generate_legend(PALETTE[:len(CATEGORIES)], DESCRIPTIONS, box_sizes=(40,...), footer=FOOTER, font_family=partial(FONT, 18),
                         max_width=450)
chart = map.place(legend, align=(1,0), padding=10)

title = Image.from_column([
Image.from_text("'CAT' IN DIFFERENT LANGUAGES", FONT(52, bold=True)),
],
bg="white")

img = Image.from_column([title, chart], bg="white", padding=2)
img = ImageEnhance.Color(img).enhance(0.7)

def sidebar(url):
    return Image.from_url_with_cache(url).crop_to_aspect(0.5).resize_fixed_aspect(height=img.height)

img2 = Image.from_row([sidebar("https://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/Cat_November_2010-1a.jpg/1200px-Cat_November_2010-1a.jpg"), img])

img2.place(Image.from_text("/u/Udzu", FONT(16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)

img2.save("output/etymcat.png")
img2.convert("RGB").save("output/etymcat.jpg", quality=90)

