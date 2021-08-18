from pudzu.charts import *

df = pd.read_csv("datasets/flagseucapitals.csv")
groups = list(remove_duplicates(df.group))
array = [[dict(r) for _,r in df.iterrows() if r.group == g] for g in groups]
data = pd.DataFrame(array, index=list(remove_duplicates(df.group)))

FONT = calibri or sans
fg, bg="black", "#EEEEEE"
default_img = "https://s-media-cache-ak0.pinimg.com/736x/0d/36/e7/0d36e7a476b06333d9fe9960572b66b9.jpg"

def process(d):
    if not d: return None
    description = get_non(d, 'description')
    description = "({})".format(description) if description else " "
    flag = Image.from_url_with_cache(get_non(d, 'image', default_img)).to_rgba()
    flag = flag.resize_fixed_aspect(height=198) if flag.width / flag.height < 1.3 else flag.resize((318,198))
    flag = flag.pad(0 if "coat" in d['group'] else (1,1,0,1) if "Slovakia" in str(d['description']) else 1, "grey")
    return Image.from_column([
      Image.from_text_bounded(d['name'].replace(r"\n","\n"), (320 if "Switzerland" not in description else 200,200), 32, partial(FONT, bold=True), beard_line=True, align="center", fg=fg),
      Image.from_text(description, FONT(24, italics=True), fg=fg),
      flag
      ], padding=2, bg=bg, equal_widths=True)

def label(r, *args, **kwargs):
    label = strip_from(data.index[r], "_")
    LABELS = ["A+", "A", "B", "C", "D", "E", "F"]
    PALETTE = [VegaPalette10[c] for c in ["purple", "blue", "green", "lightgreen", "orange", "red", "brown"]]
    color = PALETTE[LABELS.index(label)]
    return Rectangle((200,200), color).place(Image.from_text(label, FONT(48, bold=True)))

title = Image.from_text(f"European capital city flags tier list".upper(), FONT(92, bold=True), fg=fg, bg=bg).pad(40, bg)

grid = grid_chart(data, process, padding=(10,20), fg=fg, bg=bg, yalign=(0.5,1,0.5), row_label=label)
img = Image.from_column([title, grid, Rectangle((0,50))], bg=bg)
img.place(Image.from_text("/u/Udzu", FONT(24), fg=fg, bg=bg, padding=5).pad((1,1,0,0), fg), align=1, padding=5, copy=False)
img.save("output/flagseucapitals.png")

