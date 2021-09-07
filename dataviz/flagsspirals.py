from pudzu.charts import *

df = pd.read_csv("datasets/flagsspirals.csv")
groups = list(remove_duplicates(df.group))
array = [[dict(r) for _,r in df.iterrows() if r.group == g] for g in groups]
data = pd.DataFrame(array, index=list(remove_duplicates(df.group)))

FONT = calibri or sans
fg, bg="black", "#EEEEEE"
default_img = "https://s-media-cache-ak0.pinimg.com/736x/0d/36/e7/0d36e7a476b06333d9fe9960572b66b9.jpg"

W,H = 320,200

def process(d):
    if not d: return None
    description = get_non(d, 'description')
    description = "({})".format(description) if description else " "
    flag = Image.from_url_with_cache(get_non(d, 'image', default_img)).to_rgba()
    flag = flag.resize_fixed_aspect(height=H-2, width=W-2)
    flag = flag.pad(0 if "coat" in d['group'] else (1,1,0,1) if "Finland" in str(d['description']) else 1, "grey")
    flag = flag.pad_to(height=H, align=0.5, bg=bg)
    return Image.from_column([
      Image.from_text_bounded(d['name'].replace(r"\n","\n"), (W if "Switzerland" not in description else H,H), 32, partial(FONT, bold=True), beard_line=True, align="center", fg=fg),
      Image.from_text_bounded(description, (W if "Switzerland" not in description else H,H), 24, partial(FONT, italics=True), align="center", fg=fg),
      flag
      ], padding=2, bg=bg, equal_widths=True)

title = Image.from_text(f"flags with spirals".upper(), FONT(80, bold=True), fg=fg, bg=bg).pad(40, bg)
footer = Image.from_text(" ", FONT(24, italics=True), fg=fg, bg=bg).pad(20, bg)

grid = grid_chart(data, process, padding=(10,20), fg=fg, bg=bg, yalign=(0.5,1,0.5), row_label=lambda r: None if data.index[r].startswith("_") else Image.from_text("{}".format(data.index[r].replace(r"\n","\n")).upper(), FONT(32, bold=True), align="center", line_spacing=3))
img = Image.from_column([title, grid, footer], bg=bg)
img.place(Image.from_text("/u/Udzu", FONT(24), fg=fg, bg=bg, padding=5).pad((1,1,0,0), fg), align=1, padding=5, copy=False)
img.save("output/flagsspirals.png")

