from pudzu.charts import *
from pudzu.pillar import *
from pathlib import Path

SRC = "tiertimeloop"

TITLE = {
    "tiermagicschool": "PF series with an academy setting",
    "tiertimeloop": "time loop/regression PF",
}[SRC]

ranks = "SABCDF"
max_row = 10
include_empty = False
df = pd.read_csv(f"datasets/{SRC}.csv")
ldict = {
    "D": "haven't\nread\nyet",
    "F": "haven't\nread yet\n(but on hiatus)"
}

# TODO: rewrite all of this!
array = [x for r in ranks for x in list(generate_batches([[]] if df[df.tier == r].img.empty and include_empty else df[df.tier == r].img, max_row))]
indices = [(r, i) for r in ranks for i,x in enumerate(list(generate_batches([[]] if df[df.tier == r].img.empty and include_empty else df[df.tier == r].img, max_row)))]
data = pd.DataFrame(array, index=indices)
overlays = pd.DataFrame([x for r in ranks for x in list(generate_batches([[]] if df[df.tier == r].img.empty and include_empty
                         else df[df.tier == r].overlay.replace(np.nan, None),
                         max_row))])


FONT = calibri or sans
fg, bg= "white", "#020202"
default_img = "https://s-media-cache-ak0.pinimg.com/736x/0d/36/e7/0d36e7a476b06333d9fe9960572b66b9.jpg"

def process(d, r, c):
    img = Image.from_url_with_cache(d).resize((200, 300)) if d else Rectangle((200, 300), "#1a1a17")
    if overlays[c][r] is not None:
        img = img.place(Image.from_text(overlays[c][r], FONT(24, bold=True), max_width=180, align="center").add_shadow("white", blur=2))
    return img.pad((0,2), bg)

def label(r, *args, **kwargs):
    index = data.index[r]
    label = ldict.get(index[0], index[0]) if index[1] == 0 else " "
    LABELS = ["S", "A", "B", "C", "D", "F"]
    PALETTE = ["#ff7f7f", "#febf7e", "#ffff7f", "#7ffe7f", "#7fbfff", "#ff7eff"]
    color = PALETTE[LABELS.index(index[0])]
    txt = Image.from_text_bounded(label, (200, 300), 48, partial(FONT, bold=True), max_width=200, padding=10, align="center")
    img = Rectangle((200,300), color).place(txt)
    img = img.pad((0,2,0,0), bg if index[1] == 0 else color)
    img = img.pad((0,0,0,2), bg if r == len(data) - 1 or data.index[r+1][0] != index[0] else color)
    return img.pad((4,0), bg)

title = Image.from_text(TITLE.upper(), FONT(48, bold=True), fg=fg, bg=bg).pad((0,40), bg)

grid = grid_chart(data, process, padding=0, fg=fg, bg=bg, yalign=(0.5,1,0.5), row_label=label)
img = Image.from_column([title, grid], bg=bg, xalign=0.5)
#img.place(Image.from_text("/u/Udzu", FONT(24), fg=fg, bg=bg, padding=5).pad((1,1,0,0), fg), align=1, padding=5, copy=False)
img.convert("RGB").save(f"output/{SRC}.jpg")

