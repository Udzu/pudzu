from pudzu.charts import *

df = pd.read_csv("datasets/flagstriband.csv")
df = pd.concat([pd.DataFrame(df.colours.apply(list).tolist(), columns=list("TMB")), df], axis=1).set_index("colours")

FONT, SIZE = calibri, 24
fg, bg = "black", "#EEEEEE"
COLORS = { "R": "red", "G": "green", "B": "blue", "K": "black", "W": "white", "Y": "yellow" }
W, H = 320, 200

def label(c, size):
    w, h = size
    return Rectangle((w-2, h-2), RGBA(COLORS.get(c)).blend(bg, 0.25)).pad(1, "grey") # TODO: orange
    
def process(d):
    if non(d['name']): return None
    label = Image.from_text_bounded(d['name'].replace("*","").upper(), (W,H), SIZE, partial(FONT, bold=True), beard_line=True)
    description = Image.from_text_bounded(get_non(d, 'description', " "), (W,H), SIZE, partial(FONT, italics=True), beard_line=True)
    flag = Image.from_url_with_cache(d['flag']).to_rgba()
    flag = flag.resize_fixed_aspect(height=H-2) if flag.width / flag.height < 1.3 else flag.resize((W-2,H-2))
    flag = flag.pad(1, "grey")
    flaglabel = Image.from_column([label, description, flag], padding=2, bg=bg)
    if "*" in d['name']: flaglabel = flaglabel.blend(Rectangle(flaglabel.size, bg), 0.3)
    return flaglabel

for _ in range(1): # TODO: others
    m = "W"
    ms = df[df.M == m]
    array = [[dict(ms.loc[t+m+b][["name", "description", "flag"]]) for b in "RGBKY"] for t in "RGBKY"]
    data = pd.DataFrame(array, index=list("RGBKY"), columns=list("RGBKY"))
    grid = grid_chart(data, process, padding=(10,20), fg=fg, bg=bg, yalign=1,
                      row_label=lambda row: label(data.index[row], (100, H)), col_label=lambda col: label(data.columns[col], (W,100)), corner_label=label("W", (100,100)))
