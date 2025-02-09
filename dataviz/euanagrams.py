from pudzu.charts import *
from pudzu.sandbox.bamboo import *
import seaborn as sns

df = pd.read_csv("datasets/euanagrams.csv").set_index("country")

FONT = sans

def colorfn(c):
    if c in ["Sea", "Borders"]: return "white"
    elif c not in df.index: return "#A0A0A0"
    elif df.word[c].lower() == c.lower(): return VegaPalette10.BLUE
    elif df.word[c].endswith("*"): return VegaPalette10.PINK
    elif df.word[c].endswith("+"): return VegaPalette10.PURPLE
    return VegaPalette10.LIGHTBLUE

# TODO: San Marino, colors, definitions, england

def labelfn(c,w=100,h=50):
    if c in df.index:
        label = df.word[c].strip("*+")
        text = Image.from_markup_bounded(label, (w,h), 24, partial(partial, FONT), "black", align="center", padding=2, min_font_size=7)
        return text

map2 = map_chart("maps/Europe2.png", colorfn, labelfn)
mapuk = map_chart("maps/EuropeUK.png", colorfn)

def overlay(c, wh):
    label = labelfn(c)
    if label: map.overlay(label, wh)

map = map2.overlay(mapuk.crop((100,300,400,800)), (100,300), copy=True)
overlay("Ireland", (185,600))
overlay("Wales", (250,650))
overlay(("England"), (315,660))
overlay(("Scotland"), (280,500))
overlay("San Marino", (550,920))

words = df.sort_values("word", key=lambda d: d.apply(str.swapcase)).set_index("word").definition
definitions = []
for i, (word, definition) in enumerate(words.iteritems(), 1):
    definition = Image.from_markup(f"{i}. **{word.strip('*+')}**: {definition}", partial(arial, 24), "black", "white", beard_line=True, max_width=700)
    definitions.append(definition)
words = Image.from_column(definitions, xalign=0, bg="white", padding=2)

img = Image.from_row([map, words])

# HEADER = "Highest denomination"
# LABELS = [ f"{j:,} or more" if i == 0 else f"less than {i:,}" if j == 0 else f"{j:,} or more" for i,j in generate_ngrams([0] + CUTOFFS, 2) ]
# legend = generate_legend(PALETTE[:len(CUTOFFS)],  LABELS, box_sizes=40, header=HEADER, font_family=partial(FONT, 24))
# chart = map.place(legend, align=(1,0), padding=20)
#
# NOTES = [
#     "https://upload.wikimedia.org/wikipedia/commons/3/33/HUP_100MB_1946_obverse.jpg",
#     "https://i.pinimg.com/originals/c1/93/0e/c1930efc5d360f0510865b21c30c53a3.jpg",
#     "https://i.redd.it/u7i35e3lcp701.jpg",
#     "https://pbs.twimg.com/media/Cy-daaHWEAAz3CR.jpg",
#     "https://www.leftovercurrency.com/app/uploads/2016/11/20000000-turkish-old-lira-banknote-7th-emission-group-1970-obverse-1.jpg",
# ]
# notes = Image.from_column([Image.from_url_with_cache(note).convert("RGBA").resize_fixed_aspect(width=468) for note in NOTES])
# chart = Image.from_row([notes, chart], yalign=0.5)
#
# title = Image.from_column([
# Image.from_text("HIGHEST DENOMINATION BANKNOTES BY COUNTRY", FONT(48, bold=True)),
# Image.from_text('highest face value banknotes to have been in circulation [with year first issued]', FONT(36))],
# bg="white", padding=2)
#
# footer = Image.from_markup(
# '//* the Bank of England also issues a non-circulating £100,000,000 banknote (to back the value of Scottish and Northern Irish banknotes)//'
# , partial(arial, 24), "black", "white", max_width=chart.width-20, padding=(0,5,20,15))
#
#
# img = Image.from_column([title, chart, footer], bg="white", padding=2)
# img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/euanagrams.png")
# img.convert("RGB").save("output/eubanknotes.jpg", quality=90)
