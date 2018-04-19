import sys
sys.path.append('..')
from charts import *
from bamboo import *
from PIL import ImageEnhance

df = pd.read_csv("datasets/etymcomputer.csv").set_index("language")
FONT = arial

PALETTE = [PairedClass12.RED, PairedClass12.PINK, PairedClass12.BLUE, PairedClass12.LIGHTBLUE, PairedClass12.GREEN ]
CATEGORIES = ["c", "calculate", "o", "organise", "data"]

DESCRIPTIONS = [
"""from English **computer** < Latin //computare// (“calculate”)
   //originally referred to a person who carried out calculations//""",
"""from another word referring to **calculation** or **counting**:
– Czech/Slovak: from //počítat// (“count”)
– Icelandic/Faroese: from //tal// (“number”)
– Serbian/Croatian/Slovene: from //račun// (“calculation“) < Latin //ratiō//
– Estonian: from //arvutama// (“calculate”)
– Greek: from //υπολογίζω// (“calculate”)
– Hungarian: from //számít// (“count”)
– Irish: from //ríomh// (“enumeration”)
– Romanian: from //calculer// (“calculate”)
– Welsh: from //cyfrif// (“count”)""",
"""from French **ordinateur** < Latin //ōrdināre// (“put in order”)
   //coined by philologist Jacques Perret in a 1955 letter to IBM//
– Basque: from //ordenatu// (“arrange" < ōrdināre) + //gailu// (“device”)""",
"""from another word referring to **ordering** or **organising**:
– Breton: from //urzhiata// (“put in order”)""",
"""from a word referring to **data** or **information**:
– Swedish/Latvian: from //data// < Latin //datum// (“that is given”)
– Norwegian: from //data// + //maskin// (“machine”)
– Finnish: from //tieto// (“data”) + //kone// (“machine”)
– Turkish: from //bilgi// (“information”) + //say// (“count”)"""
]
FOOTER = None
 
def colorfn(c):
    if c in ['Sea', 'Language Borders']: return "white"
    elif c in ['Country Borders']: return "#AAAAAA"
    elif c not in df.index: return "grey"
    else: return PALETTE[CATEGORIES.index(df.group.get(c))]
    
def labelfn(c, w, h):
    if c not in df.index: return None
    label = df.word[c].replace("\\n", "\n")
    return Image.from_text_bounded(label, (w, h), 24, papply(FONT, bold=True), align="center", padding=(0,0,0,2))
    
map = map_chart("maps/Eurolang.png", colorfn, labelfn)
legend = generate_legend(PALETTE[:len(CATEGORIES)], DESCRIPTIONS, box_sizes=(40,...), header="ETYMOLOGIES", footer=FOOTER, fonts=partial(FONT, 16))
chart = map.pin(legend, (map.width+2, 0), align=(0,0), bg="white")

title = Image.from_column([
Image.from_text("COMPUTER IN DIFFERENT LANGUAGES", FONT(48, bold=True)),
Image.from_text("most common terms for computer, with etymologies", FONT(36))],
bg="white")

img = Image.from_column([title, chart], bg="white", padding=2)
img = ImageEnhance.Color(img).enhance(0.7)
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/etymcomputer.png")

