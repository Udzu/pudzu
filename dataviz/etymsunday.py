import sys
sys.path.append('..')
from charts import *
from bamboo import *

df = pd.read_csv("datasets/etymsunday.csv").set_index("language")
FONT = calibri

CATEGORIES = ["s", "d", "n", "m", "r", "o"]

DESCRIPTIONS = [
"**sun day**: from Latin //dies Solis//, after the first classical planet",
"**Lord's day**: mostly from Latin //dies Dominica//, day of Christian worship",
"**no work day**: from Proto-Slavic //*nedělja//, cognate with no+do",
"**market day**: from Persian //bâzâr// via Turkish",
"**other religious terms**: holy day (//Estonian, Latvian//), ascension day (//Basque//), resurrection (//Russian//)",
"**numbered terms**: first day (//Maltese//), seventh day (//Lithuanian//)"
]
PALETTE = VegaPalette10
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
legend = generate_legend(PALETTE[:len(CATEGORIES)], DESCRIPTIONS, header="Etymologies", box_sizes=[(40,40 if len(d)<90 else 60) for d in DESCRIPTIONS], footer=FOOTER, max_width=320)
chart = map.place(legend, align=(1,0), padding=10)

title = Image.from_text("SUNDAY IN DIFFERENT LANGUAGES", FONT(60, bold=True))
img = Image.from_column([title, chart], bg="white", padding=2)
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/etymsunday.png")
