import sys
sys.path.append('..')
from charts import *
from bamboo import *

# B = born in what is now India
# b = born in what was then British India
# C = citizen of India or British India at time of award
# c = citizen of India or British India prior to award
# r = resident in India at time of award
# o = person of Indian origin

FONT = calibri
df = pd.read_csv("datasets/nobelsindian.csv")
table = pd.DataFrame([[first_or_default([dict(d) for _,d in df[(df.grid_x == x) & (df.grid_y == y)].iterrows()]) for x in range(df.grid_x.max()+1)] for y in range(df.grid_y.max()+1)])

default_img = "https://s-media-cache-ak0.pinimg.com/736x/0d/36/e7/0d36e7a476b06333d9fe9960572b66b9.jpg"
FONT = verdana
PALETTE = CaseInsensitiveDict({"B": VegaPalette10.BLUE, "C": VegaPalette10.GREEN, "R": VegaPalette10.GREY, "O": VegaPalette10.BROWN })
ALPHA = {"B": 128, "b": 64, "C": 128, "c": 64, "r": 64, "o": 64 }

def box(g, n):
    i = Image.new("RGBA", (40,40), "white")
    for g in set([g, g.lower()]):
        i = i.place(Image.new("RGBA", (40,40), RGBA(PALETTE[g])._replace(alpha=ALPHA[g])))
    i = i.place(Image.from_text(str(n), FONT(14, bold=True)))
    return i

legend = generate_legend(
[box(c, "+"*(c in "bc") + str(len(df.filter_rows("group >> {}".format(c))))) for c in "CcBbor"], 
["Citizen of India or British India at the time of award.",
 "Citizen of India or British India //prior// to the award.",
 "Born in what is now India.",
 "Born in what was //then// British India.",
 "Person of Indian Origin at the time of award.",
 "Resident of India at the time of award."], fonts=partial(FONT, 14), max_width=250, header="Categories").pad(4, "white")

def process(d):
    if d is None: return legend
    return Image.from_column([
      Image.from_text_bounded(d['name'], (200,40), 18, partial(FONT, bold=True)),
      Image.from_markup("//{}//, //{}//".format(d['field'], d['year']), papply(FONT, 16)),
      Image.from_url_with_cache(get_non(d, "image", default_img)).cropped_resize((200,250), (0.5,0.25))
      ], padding=2, yalign=1).pad((0,4), 0)
      
def group(d):
    if d is None: return None
    return sorted(set(d['group']) | set(d['group'].lower()))

grid = grid_chart(table, process, group, padding=10, yalign=0, group_rounded=True, group_padding=4, group_colors=PALETTE, group_alpha=ALPHA, bg="white")

title = Image.from_text("India-linked Nobel Laureates".upper(), FONT(48, bold=True))
img = Image.from_column([title, grid], bg="white", padding=10)
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.convert("RGB").save("output/nobelsindian.jpg")
