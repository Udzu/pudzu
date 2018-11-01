from pudzu.charts import *
from pudzu.bamboo import *
import seaborn as sns

df = pd.read_csv("datasets/euukinvasions.csv").set_index('country')

invaded = RGBA(204,85,85,255)
parent = tmap(RGBA, sns.color_palette("Reds", 4))[1] #RGBA(204,125,85,255)
supported = tmap(RGBA, sns.color_palette("Greens", 4))[-2]

def colorfn(c):
    if c in ['Sea', 'Borders']: return "white"
    elif c not in df.index: return "#AAAAAA"
    elif df.loc[c].type == "invaded": return invaded
    elif df.loc[c].type == "parent": return parent
    elif df.loc[c].type == "supported": return supported
    else: return "white"
    
def labelfn(c, w, h):
    # TODO: better label handling!
    s = ignoring_exceptions(lambda : get_non(df.loc[c], "battle"))()
    return Image.from_text(s, arial(14, bold=False), "black", max_width=w, align="center", padding=(0,0,0,2)) if s else s
    
map = map_chart("maps/Europe.png", colorfn, labelfn)

# generate legend
font_size = 16
def box(c, box_size=30): return Image.new("RGBA", (box_size, box_size), c)

year_arr = Image.from_array([
[box(invaded), Image.from_text("Attack against state", arial(font_size), padding=(10,0))],
[box(parent), Image.from_text("Attack against parent", arial(font_size), padding=(10,0))],
[box(supported), Image.from_text("Supported state", arial(font_size), padding=(10,0))]
], bg="white", xalign=0)
year_leg = Image.from_column([Image.from_text("Type of attack", arial(font_size, bold=True)), year_arr], bg="white", xalign=0, padding=(0,5))
note_leg = Image.from_text("Attacks refer to any hostile military actions in the territory of the state.\n\nParent attacks refers to actions in the state when it was under the control of another country (e.g. the Russian Empire).\n\nSupporting actions, like attacks, only include military actions in the territory of the state.", arial(font_size), max_width=200, bg="white", padding=(0,2))
legend = Image.from_column([year_leg, note_leg], bg="white", xalign=0, padding=5).pad(1, "black")

chart = map.place(legend, align=(1,0), padding=10)
title = Image.from_text("European countries attacked by Britain", arial(60, bold=True), "black", "white")
footer = Image.from_text("also: technically at war with Sweden from 1810-12 but no shots were fired; accidentally bombed Switzerland during WWII; bombed East Prussia before it became part of Poland", arial(14), "black", "white", padding=(0,5,20,5)) #max_width=chart.width-150

img = Image.from_column([title, chart, footer], bg="white")
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/euukinvasions.png")