from pudzu.charts import *
from pudzu.sandbox.bamboo import *

df = pd.read_csv("datasets/euworldchamps.csv").set_index("sport").split_columns(["men", "women"], "|")
FONT = calibri
FONT = partial(font, "/usr/share/fonts/truetype/freefont/FreeSans")

EXCOUNTRIES = { "USSR": { "Russia", "Latvia", "Estonia", "Lithuania", "Belarus", "Ukraine", "Georgia", "Azerbaijan", "Kazakhstan", "Armenia" },
"Yugoslavia": {"Slovenia", "Croatia", "Bosnia", "Macedonia", "Serbia", "Kosovo", "Montenegro"},
"Czechoslovakia": {"Czech Republic", "Slovakia"},
"UK": { "England", "Scotland", "Wales", "Northern Ireland"}
}
SPORTS = list(df.index)
PALETTE = [VegaPalette10.RED, VegaPalette10.BLUE, VegaPalette10.GREEN, VegaPalette10.ORANGE, VegaPalette10.PURPLE, VegaPalette10.LIGHTBLUE, VegaPalette10.LIGHTGREEN, VegaPalette10.BROWN, VegaPalette10.PINK]
SIZE = 8

def fade(color):
    return RGBA(color).blend("#AAAAAA", 0.65)
    
def pattern(colors, width, height):
    p = Image.from_column([Rectangle([10,SIZE], c) for i,c in enumerate(colors)])
    # TODO: better way of creating diagonal stripes
    sz = max(width, height)
    return Image.from_pattern(p, (sz*4, sz*4)).rotate(30, Image.BILINEAR).crop((sz,sz,sz+width,sz+height))

def colorfn(c, width, height, men=True):
    print(c)
    if c in ['Sea', 'Borders']: return "white"
    colors = []
    for sport, winners in df['men' if men else 'women'].iteritems():
        exwinners = { x for c in winners if c in EXCOUNTRIES for x in EXCOUNTRIES[c] }
        if c in winners or c in exwinners and c in EXCOUNTRIES["UK"]: colors.append(PALETTE[SPORTS.index(sport)])
        elif c in exwinners: colors.append(fade(PALETTE[SPORTS.index(sport)]))
    if len(colors) == 0: return "#AAAAAA"
    return pattern(colors, width, height)
    
map1 = map_chart("maps/EuropeUK.png", colorfn, resize_patterns=True)
map2 = map_chart("maps/EuropeUK.png", partial(colorfn, men=False), resize_patterns=True)

legend = generate_legend([Image.from_row([Rectangle(40, c)]) for c in PALETTE],
                         [sport.title() for sport in SPORTS], font_family=partial(FONT, size=16),
                         header="World Championship", footer="(faded colors indicate victories as part of a former country)", max_width=180)
chart1 = map1.place(legend, align=(1,0), padding=10)
chart2 = map2.place(legend, align=(1,0), padding=10)

title1 = Image.from_text("Europe’s World Champions (Men)".upper(), FONT(48, bold=True))
title2 = Image.from_text("Europe’s World Champions (Women)".upper(), FONT(48, bold=True))

img1 = Image.from_column([title1, chart1], bg="white", padding=2)
img2 = Image.from_column([title2, chart2], bg="white", padding=2)

img = Image.from_row([img1, img2])
img.place(Image.from_text("/u/Udzu", FONT(16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/euworldchamps.png")

