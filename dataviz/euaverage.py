from pudzu.charts import *
from pudzu.experimental.bamboo import *
from statistics import mean
import seaborn as sns

# generate map
flags = pd.read_csv("datasets/countries.csv").split_columns(('nationality', 'tld', 'country'), "|").explode('country').set_index('country')

def colorfn(c):
    if c not in flags.index: # or flags['continent'][c] != 'Europe':
        return "white" if c in ['Sea', 'Borders'] else "grey"
    flag_array = np.array(Image.from_url_with_cache(flags['flag'][c]).convert("RGB")) / 256
    float_average = [ math.sqrt((flag_array[:,:,i] ** 2).mean()) for i in range(flag_array.shape[-1])]
    return RGBA(int(256 * f) for f in float_average)

scores = { "AEIOULNSTR": 1, "DG": 2, "BCMP": 3, "FHVWY": 4, "K": 5, "JX": 8, "QZ": 10 }
scores = { l : s for ls,s in scores.items() for l in ls }

def score_country(c):
    c = { 'Bosnia': 'Bosnia and Herzegovina', 'UK': 'United Kingdom' }.get(c, c)
    return str(sum(scores.get(l,0) for l in c.upper()))

def average_country(c):
    if c == 'Czech Republic': c = 'Czechia'
    return chr(int(mean(ord(c) for c in c.upper())))
   
label_fn = score_country

map = map_chart("maps/Europe.png", colorfn, label_fn, label_font=arial(16, bold=True))

# legend
def flag(c): return Image.from_url_with_cache(flags['flag'][c]).resize_fixed_aspect(width=50).place(Image.from_text(c, arial(16, bold=True), "black"))
def box(c): return Image.new("RGBA", (50, 30), colorfn(c)).place(Image.from_text(label_fn(c), arial(16, bold=True), "black", bg=colorfn(c)))

flag_leg = Image.from_array([[flag('Malta'), Image.from_text("flag", arial(16))],
[box('Malta'), Image.from_text("average\n+ score", arial(16))]
], bg="white", xalign=0, padding=(5,5))

note_leg = Image.from_text("Flag images and common English names both from Wikipedia.", arial(16), max_width=120, bg="white", padding=(0,2))

legend = Image.from_column([flag_leg, note_leg], bg="white", xalign=0, padding=5).pad(1, "black")
chart = map.place(legend, align=(1,0), padding=10)

# title
title = Image.from_column([
Image.from_text("EUROPE: THE ESSENTIAL FACTS", arial(48, bold=True)),
Image.from_text("average flag colours and Scrabble name scores", arial(36))],
bg="white")
img = Image.from_column([title, chart], bg="white", padding=2)
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/euaverage.png")
