from pudzu.charts import *
from pudzu.experimental.bamboo import *

df = pd.read_csv("datasets/eurovision_votes.csv").set_index("country")
countries = pd.read_csv("datasets/countries.csv").split_columns(('nationality', 'tld', 'country'), "|").explode('country').set_index('country')

RANGES = [12, 10, 8, 6, 4, 2]
LABELS = ["twelve points (douze points)", ">ten points (dix points)", ">eight points (huit points)", ">six points (six points)", ">four points (quatre points)", ">two points (deux points)"]
PALETTE_TO = treversed(['#eff3ff','#c6dbef','#9ecae1','#6baed6','#4292c6','#2171b5','#084594'])
PALETTE_FROM = PALETTE_TO 
FONT = calibri

def colorfn(c, to=True):
    if c in ['Sea', 'Borders']: return 'white'
    elif c not in df.index: return "grey"
    return first(PALETTE_TO[i] if to else PALETTE_FROM[i] for i in range(len(RANGES)) if (df.to_score[c] if to else df.from_score[c]) >= RANGES[i])
    
def labelfn(c, w, h, *args, to=True):
   if c not in df.index: return None
   flag = Image.from_url_with_cache(countries.flag[df.to[c] if to else df['from'][c]]).to_rgba().resize((24,18))
   country = Image.from_text(df.to[c] if to else df['from'][c], FONT(16), "black")
   score = Image.from_text("{0:.1f}".format(df.to_score[c] if to else df.from_score[c]), FONT(16), "black")
   return first(i for i in [Image.from_row([flag, Rectangle(5,0), score]), flag] if i.width <= w)

map_from = map_chart("maps/Europe2.png", partial(colorfn, to=False), partial(labelfn, to=False))
legend_from = generate_legend(PALETTE_FROM[:len(RANGES)], LABELS, header="HIGHEST AVERAGE POINTS RECEIVED", box_sizes=40, fonts=partial(FONT, 16))
chart_from = map_from.place(legend_from, align=(1,0), padding=10)

map_to = map_chart("maps/Europe2.png", partial(colorfn, to=True), partial(labelfn, to=True))
legend_to = generate_legend(PALETTE_FROM[:len(RANGES)], LABELS, header="HIGHEST AVERAGE POINTS GIVEN", box_sizes=40, fonts=partial(FONT, 16))
chart_to = map_to.place(legend_to, align=(1,0), padding=10)

chart = Image.from_row([chart_to, chart_from])

title = Image.from_column([
Image.from_text("Eurovision friendships: highest average points given (←) and received (→) per country".upper(), FONT(60, bold=True)),
Image.from_text("excludes ex-countries (Yugoslavia, S&M) and countries with <5 appearances (Morroco, Australia)", FONT(48, italics=True))],
bg="white", padding=4)
img = Image.from_column([title, chart], bg="white", padding=10)

img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/eurovision_votes.png")
