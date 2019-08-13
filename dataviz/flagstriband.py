from pudzu.charts import *

df = pd.read_csv("datasets/flagstriband.csv")
df = pd.concat([pd.DataFrame(df.colours.apply(list).tolist(), columns=list("TMB")), df], axis=1).set_index("colours")

for _ in range(1):
    m = "W"
    ms = df[df.M == m]
    array = [[dict(ms.loc[t+m+b][["name", "flag"]]) for b in "RGBKY"] for t in "RGBKY"]
    data = pd.DataFrame(array, index=list("RGBKY"), columns=list("RGBKY"))

FONT = calibri
fg, bg="black", "#EEEEEE"

def label(c, size):
    colours = { "R": "red", "G": "green", "B": "blue", "K": "black", "W": "white", "Y": "yellow" }
    flag = Rectangle(size, RGBA(colours.get(c)).blend(bg, 0.25)).pad(1, "grey") # TODO: yellow/orange/brown
    label = Image.from_text(" ", FONT(20, bold=True), beard_line=True)
    flaglabel = Image.from_column([label, flag], padding=2)
    return flaglabel
    
def process(d):
    if non(d['name']): return None
    label = Image.from_text(d['name'].replace("*","").upper(), FONT(20, bold=True), beard_line=True)
    flag = Image.from_url_with_cache(d['flag']).to_rgba()
    flag = flag.resize_fixed_aspect(height=198) if flag.width / flag.height < 1.3 else flag.resize((318,198))
    flag = flag.pad(1, "grey")
    flaglabel = Image.from_column([label, flag], padding=2, bg=bg)
    if "*" in d['name']:
        flaglabel = flaglabel.blend(Rectangle(flaglabel.size, bg), 0.35)
    return flaglabel
    
grid = grid_chart(data, process, padding=(10,20), fg=fg, bg=bg, yalign=(0.5,0.5,0.5),
                  row_label=lambda row: label(data.index[row], (98,198)), col_label=lambda col: label(data.columns[col], (318,98)))
