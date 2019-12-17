from pudzu.charts import *
from pudzu.experimental.bamboo import *
from PIL import ImageEnhance

df = pd.read_csv("datasets/euendian.csv").set_index("country")

FONT = arial
PALETTE = [VegaPalette10.BLUE, VegaPalette10.ORANGE, VegaPalette10.BROWN]
CATEGORIES = ["l", "m", "b"]

def colorfn(c, group):
    cols = ValueBox()
    if c in ['Sea', 'Borders']: return "white"
    elif c not in df.index: return "grey"
    elif len(cols << [PALETTE[CATEGORIES.index(x)] for x in df[group].get(c)]) == 1: return cols()[0]
    else: return Stripe(10, cols()[0], cols()[1])
    
date_eu = map_chart("maps/Europe.png", partial(colorfn, group="date"))
date_us = map_chart("maps/USA.png", lambda c: "white" if c in ['Sea', 'Borders'] else PALETTE[CATEGORIES.index("m")]).trim((0,0,50,0))
date_legend = generate_legend(PALETTE, [
"Little endian: e.g. 14.07.1789",
"Middle endian: e.g. 07.14.1789",
"Big endian: e.g. 1789.07.14"
], header="Year/Month/Day ordering".upper(), fonts=partial(FONT, 32))
date_map = Image.from_row([date_us, date_eu.place(date_legend, align=(1,0), padding=10)], bg="white")

address_eu = map_chart("maps/Europe.png", partial(colorfn, group="address"))
address_us = map_chart("maps/USA.png", lambda c: "white" if c in ['Sea', 'Borders'] else PALETTE[CATEGORIES.index("l")]).trim((0,0,50,0))
address_legend = generate_legend(PALETTE, [
"Little-endian: e.g. 10 Downing Street, London",
"Middle-endian: e.g. Prinsengracht 263, Amsterdam",
"Big-endian: e.g. Budapest, Dísz tér 11"
], header="City/Street/Number ordering".upper(), fonts=partial(FONT, 32))
address_map = Image.from_row([address_us, address_eu.place(address_legend, align=(1,0), padding=10)])

date_title = Image.from_column([
Image.from_text("DATE FORMAT ENDIANNESS", FONT(96, bold=True)), 
Image.from_text("(preferred format according to ICU locales)", FONT(54, italics=True))
], padding=5)

address_title = Image.from_column([
Image.from_text("ADDRESS FORMAT ENDIANNESS", FONT(96, bold=True)), 
Image.from_text("(preferred format according to the Universal Postal Union)", FONT(54, italics=True))
], padding=5)

img = Image.from_column([date_title, date_map, address_title, address_map], bg="white", padding=5)
img = ImageEnhance.Color(img).enhance(0.7)
#img.place(Image.from_text("/u/Udzu", font("arial", 24), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/euendian.png")

