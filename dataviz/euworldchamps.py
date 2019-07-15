from pudzu.charts import *
from pudzu.bamboo import *

df = pd.read_csv("datasets/euworldchamps.csv").set_index("sport").split_columns(["men", "women"], "|")
FONT = calibri

EXCOUNTRIES = { "USSR": { "Russia", "Latvia", "Estonia", "Lithuania", "Belarus", "Ukraine", "Georgia", "Azerbaijan", "Kazakhstan", "Armenia" },
"Yugoslavia": {"Slovenia", "Croatia", "Bosnia", "Macedonia", "Serbia", "Kosovo", "Montenegro"},
"Czechoslovakia": {"Czech Republic", "Slovakia"},
"UK": { "England", "Scotland", "Wales", "Northern Ireland"}
}
SPORTS = list(df.index)
PALETTE = [VegaPalette10.RED, VegaPalette10.BLUE, VegaPalette10.GREEN, VegaPalette10.ORANGE, VegaPalette10.PURPLE, VegaPalette10.LIGHTGREEN, VegaPalette10.BROWN, VegaPalette10.PINK]
SIZE = 25

def fade(color):
    return RGBA(color).blend("#AAAAAA", 0.5)
    
def pattern(colors):
    p = Image.from_column([Rectangle([10,(SIZE*(i+1))//len(colors)-(SIZE*i)//len(colors)], c) for i,c in enumerate(colors)])
    return p
    #return Image.from_pattern(p, (2000, 2000)).rotate(30, Image.BILINEAR).crop((500,500,1500,1500))

def colorfn(c, *args, men=True):
    print(c)
    if c in ['Sea', 'Borders']: return "white"
    colors = []
    for sport, winners in df['men' if men else 'women'].iteritems():
        exwinners = { x for c in winners if c in EXCOUNTRIES for x in EXCOUNTRIES[c] }
        if c in winners or c in exwinners and c in EXCOUNTRIES["UK"]: colors.append(PALETTE[SPORTS.index(sport)])
        elif c in exwinners: colors.append(fade(PALETTE[SPORTS.index(sport)]))
    if len(colors) == 0: return "#AAAAAA"
    return pattern(colors)
    
map1 = map_chart("maps/EuropeUK.png", colorfn)
map2 = map_chart("maps/EuropeUK.png", partial(colorfn, men=False))

legend = generate_legend([Image.from_row([Rectangle(40, c)]) for c in PALETTE],
                         [sport.title() for sport in SPORTS], font_family=partial(FONT, size=16),
                         header="Sport", footer="faded colors correspond to ex countries", max_width=150)
chart1 = map1.place(legend, align=(1,0), padding=10)
chart2 = map2.place(legend, align=(1,0), padding=10)
chart = Image.from_row([chart1, chart2])