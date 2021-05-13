from pudzu.charts import *
from pudzu.sandbox.bamboo import *
from PIL import ImageEnhance

df = pd.read_csv("datasets/etymsmith.csv").set_index("language").fillna("")
FONT = arial
UFONT = partial(font, "fonts/arialu")
LFONT = lambda l: FONT if l not in ["Georgian", "Armenian", "Arabic", "Hebrew", "Persian"] else UFONT

PALETTE = [VegaPalette10.RED, VegaPalette10.BLUE, VegaPalette10.LIGHTBLUE, VegaPalette10.GREEN, VegaPalette10.LIGHTGREEN, VegaPalette10.ORANGE, VegaPalette10.PINK, VegaPalette10.BROWN, VegaPalette10.GREY]
CATEGORIES = ["s", "f", "F", "k", "K", "g", "S", "d", ""]

DESCRIPTIONS = [
" from Proto-Germanic //*smiþaz// (“craftsman, smith”)",
" from Latin //ferrārius// (“ironsmith”), from //ferrum// (“iron”)",
" from Latin //faber// (“craftsman”)",
" from Proto-Slavic //*kovati// (“to forge”)",
" from Proto-Balto-Slavic *kolʔ- (“to hammer””)",
" from Proto-Celtic //*goban// (“smith”)",
" from Proto-Finnic //*seppä// (“smith”)",
" from Proto-Turkic //*temürči// (“blacksmith”)",
" from various other roots"
]
HEADER = "Etymology"
FOOTER = None
 
def colorfn(c):
    cols = ValueBox()
    if c in ['Sea', 'Language Borders']: return "white"
    elif c in ['Country Borders']: return "#AAAAAA"
    elif c not in df.index: return "grey"
    elif len(cols << [PALETTE[CATEGORIES.index(x)] for x in df.group.get(c)]) == 1: return cols()[0]
    elif df.word[c]: return "grey"
    else: return "#AAAAAA"
    
def labelfn(c, w, h):
    if c not in df.index: return None
    label = df.word[c].replace("\\n", "\n")
    return Image.from_text_bounded(label, (w, h), 24, papply(LFONT(c), bold=True), align="center", padding=(0,0,0,2))
    
map = map_chart("maps/Eurolang2.png", colorfn, labelfn)
legend = generate_legend(PALETTE[:len(CATEGORIES)], DESCRIPTIONS, box_sizes=(40,...), header=HEADER, footer=FOOTER, font_family=partial(FONT, 16))
chart = map.place(legend, align=(1,0))

title = Image.from_column([
Image.from_text("SMITH IN DIFFERENT EUROPEAN LANGUAGES", FONT(48, bold=True)),
Image.from_text("the most common forms of the occupational surname", FONT(36))],
bg="white")

img = Image.from_column([title, chart], bg="white", padding=2)
img = ImageEnhance.Color(img).enhance(0.7)
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/etymsmith.png")

