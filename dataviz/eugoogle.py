from pudzu.charts import *
from pudzu.sandbox.bamboo import *
import seaborn as sns

df = pd.read_csv("datasets/eugoogle.csv").set_index('country')
palette = tmap(RGBA, sns.color_palette())

def colorfn(c, type, bg):
    if c in ['Sea', 'Borders']: return "white"
    elif ignoring_exceptions(lambda : get_non(df.loc[c], type))(): return bg
    else: return "#AAAAAA"
    
def labelfn(c, w, h, type):
    # TODO: better label handling!
    s = ignoring_exceptions(lambda : get_non(df.loc[c], type, "?"))()
    return Image.from_text(s, arial(14, bold=True), "black", max_width=w, align="center", padding=(0,0,0,2)) if s else s
    
cs = []
for n, type in enumerate(["whyisXso", "whyisX", "whyareXian", "isXbetterthan"]):
    chart = map_chart("maps/Europe.png", partial(colorfn, type=type, bg=palette[n]), partial(labelfn, type=type))
    if type == "whyisXso":
        TITLE = "Why is X so ...?"
        SUBTITLE = "excludes rich/poor/big/small/expensive/cheap"
    elif type == "whyisX":
        TITLE = "Why is X ...?"
        SUBTITLE = "excludes 'Why is X so ...?' and 'Why is X called X?'"
    elif type == "whyareXian":
        TITLE = "Why are X-ian ...?"
        SUBTITLE = ""
    elif type == "isXbetterthan":
        TITLE = "Is X better than ...?"
        SUBTITLE = ""
    
    title = Image.from_text("Top Google UK autocomplete for '{}'".format(TITLE), arial(36, bold=True), "black", padding=(0,5,0,0))
    subtitle = Image.from_text(SUBTITLE, arial(24, bold=True), "black")
    chart = Image.from_column([title, subtitle, chart], bg="white")
    cs.append(chart)
    
img = Image.from_array([cs[:2], cs[2:]], bg="white", yalign=0)
title = Image.from_text("How the UK sees the rest of Europe, according to Google", arial(60, bold=True), "black", "white")
img = Image.from_column([title, img], bg="white")
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/eugoogle.png")