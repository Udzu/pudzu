from pudzu.charts import *
from pudzu.experimental.bamboo import *

FONT = verdana
ORDER = "gecfbv"
COL_LABELS = { "g": "partly European geographically",
"e": "in the European Union",
"c": "in the Council of Europe",
"f": "has participated in the Euros",
"b": "has particpated in Eurobasket",
"v": "has participated in Eurovision" }
COL_IMAGES = { "g": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Europe_orthographic_Caucasus_Urals_boundary_%28with_borders%29.svg/1026px-Europe_orthographic_Caucasus_Urals_boundary_%28with_borders%29.svg.png", 
"e": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b7/Flag_of_Europe.svg/1024px-Flag_of_Europe.svg.png",
"c": "https://upload.wikimedia.org/wikipedia/en/d/d9/Council_of_Europe_logo_%282013_revised_version%29.png",
"f": "https://upload.wikimedia.org/wikipedia/en/thumb/9/96/UEFA_Euro_2020_Logo.svg/900px-UEFA_Euro_2020_Logo.svg.png",
"b": "https://upload.wikimedia.org/wikipedia/en/5/50/EuroBasket_2017_logo.png",
"v": "https://www.underconsideration.com/brandnew/archives/eurovision_logo_detail.png" }
YES = Image.open("icons/yes.png").pad(150, "white").resize((50,50))
NO = Image.open("icons/no.png").pad(150, "white").resize((50,50))

df = pd.read_csv("datasets/eunotquite.csv")
atlas = pd.read_csv("datasets/countries.csv").split_columns('country', "|").explode('country').set_index("country")
data = pd.DataFrame([{ k : k in d.groups for k in ORDER } for _,d in df.iterrows() ], index=df.country, columns=list(ORDER))

FOOTER = "Designed by Milano83 / Freepik"

def rlabel_fn(r, v):
    return Image.from_row([
        Image.from_text(data.index[r].upper(), FONT(16, bold=True)),
        Image.from_url_with_cache(atlas.flag[data.index[r]]).convert("RGBA").resize((60,40)).trim(1).pad(1, "grey")
    ], padding=(4,0)).pad((0,5), "white")
    
def clabel_fn(c, v):
    return Image.from_column([
        Image.from_url_with_cache(COL_IMAGES[data.columns[c]]).convert("RGBA").pad_to_aspect(80,50, bg="white").resize((80,50)),
        Image.from_text("({})".format(COL_LABELS[data.columns[c]]), FONT(10, bold=True), max_width=80, hyphenator=language_hyphenator())
    ], padding=(0,4))

# grid_chart(data, lambda b: [NO,YES][b].pad_to_aspect(80,50, bg="white"), label_font=arial(16), bg="white", xalign=1, yalign=0)

grid = grid_chart(data, lambda b: [NO,YES][b].pad_to_aspect(80,50, bg="white"), row_label=rlabel_fn, col_label=clabel_fn, bg="white", xalign=1, yalign=0)

title = Image.from_column([
Image.from_text("Non-European countries in Europe".upper(), FONT(28, bold=True)),
Image.from_text("(countries where most of the population live outside the prevalent geographic\nborder of Europe that follows the Urals, Caucasus Mountains and Turkish Straits)", FONT(18), align="center")
], bg="white", padding=2)
img = Image.from_column([title, grid, Rectangle((0,25))], bg="white", xalign=0.5, padding=10)
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/eunotquite.png")
