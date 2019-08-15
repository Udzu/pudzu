from pudzu.charts import *

df = pd.read_csv("datasets/flagstriband.csv")
df = pd.concat([pd.DataFrame(df.colours.apply(list).tolist(), columns=list("TMB")), df], axis=1).set_index("colours")

FONT, SIZE = calibri, 24
fg, bg = "black", "#EEEEEE"
default_img = "https://s-media-cache-ak0.pinimg.com/736x/0d/36/e7/0d36e7a476b06333d9fe9960572b66b9.jpg"
COLORS = { "R": "red", "G": "green", "B": "blue", "K": "black", "W": "white", "Y": "yellow" }
W, H = 320, 200

def label(c, size):
    w, h = size
    label = Image.from_text_bounded(" ", (W,H), SIZE, partial(FONT, bold=True), beard_line=True)
    description = Image.from_text_bounded(" ", (W,H), SIZE, partial(FONT, italics=True), beard_line=True)
    flag = Rectangle((w-2, h-2), RGBA(COLORS.get(c)).blend(bg, 0.25)).pad(1, "grey") # TODO: orange
    return Image.from_column([label, description, flag], padding=2, bg=bg)
    
def process(d):
    if non(d['name']): return None
    label = Image.from_text_bounded(d['name'].replace("*","").upper(), (W,H), SIZE, partial(FONT, bold=True), beard_line=True)
    description = Image.from_text_bounded(get_non(d, 'description', " "), (W,H), SIZE, partial(FONT, italics=True), beard_line=True)
    flag = Image.from_url_with_cache(get_non(d, 'flag', default_img)).to_rgba()
    flag = flag.resize_fixed_aspect(height=H-2) if flag.width / flag.height < 1.3 else flag.resize((W-2,H-2))
    flag = flag.pad(1, "grey")
    flaglabel = Image.from_column([label, description, flag], padding=2, bg=bg)
    if "*" in d['name']: flaglabel = flaglabel.blend(Rectangle(flaglabel.size, bg), 0.3)
    return flaglabel

def grid(middle):
    ms = df[df.M == middle]
    colors = "".join(COLORS).replace(middle,"")
    array = [[dict(ms.loc[t+middle+b][["name", "description", "flag"]]) for b in colors] for t in colors]
    data = pd.DataFrame(array, index=list(colors), columns=list(colors))
    grid = grid_chart(data, process, padding=(10,20), fg=fg, bg=bg, yalign=1,
                      row_label=lambda row: label(data.index[row], (100, H)), col_label=lambda col: label(data.columns[col], (W,100)), corner_label=label(middle, (100,100)))
    return grid

grids = list(generate_batches([grid(c) for c in "WRGBKY"], 3))
grid = Image.from_array(grids, padding=20, bg=bg)
title = Image.from_text("A compendium of horizontal triband flags".upper(), FONT(240, bold=True), fg=fg, bg=bg).pad(40, bg)
img = Image.from_column([title, grid], bg=bg, padding=(20,0))
img.place(Image.from_text("/u/Udzu", FONT(24), fg=fg, bg=bg, padding=5).pad((1,1,0,0), fg), align=1, padding=5, copy=False)
img.save("output/flagstriband.png")
