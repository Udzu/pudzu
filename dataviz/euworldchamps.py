from pudzu.charts import *
from pudzu.bamboo import *

# generate map
df = pd.read_csv("datasets/euworldchamps.csv").set_index("sport").split_columns(["men", "women"], "|")
FONT = calibri

EXCOUNTRIES = { "USSR": { "Russia", "Latvia", "Estonia", "Lithuania", "Belarus", "Ukraine", "Georgia", "Azerbaijan", "Kazakhstan", "Armenia" },
"Yugoslavia": {"Slovenia", "Croatia", "Bosnia", "Macedonia", "Serbia", "Kosovo", "Montenegro"},
"Czechoslovakia": {"Czech Republic", "Slovakia"},
"UK": { "England", "Scotland", "Wales", "Northern Ireland"}
}
SPORTS = list(df.index)
PALETTE = VegaPalette10

def colorfn(c, *args, men=True):
    print(c)
    if c in ['Sea', 'Borders']: return "white"
    colors = []
    for sport, winners in df['men' if men else 'women'].iteritems():
        exwinners = { x for c in winners if c in EXCOUNTRIES for x in EXCOUNTRIES[c] }
        if c in winners or c in exwinners and c in EXCOUNTRIES["UK"]: colors.append(VegaPalette10[SPORTS.index(sport)])
        elif c in exwinners: colors.append(VegaPalette10[SPORTS.index(sport)].blend("grey", 0.6))
    if len(colors) == 0: return "grey"
    else: return Image.from_column([Rectangle([10,10], c) for c in colors])
    
map = map_chart("maps/EuropeUK.png", colorfn)
