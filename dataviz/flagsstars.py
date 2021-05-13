from pudzu.charts import *

df = pd.read_csv("datasets/flagsstars.csv")
groups = list(remove_duplicates(df.group))
array = [[dict(r) for _,r in df.iterrows() if r.group == g] for g in groups]
data = pd.DataFrame(array, index=list(remove_duplicates(df.group)))

FONT = calibri
W,H = 320,200
fg, bg="black", "#EEEEEE"
default_img = "https://s-media-cache-ak0.pinimg.com/736x/0d/36/e7/0d36e7a476b06333d9fe9960572b66b9.jpg"

def process(d):
    if not d: return None
    description = get_non(d, 'description', " ")
    flag = Image.from_url_with_cache(get_non(d, 'image', default_img)).to_rgba()
    flag = flag.resize_fixed_aspect(height=H-2) if flag.width / flag.height < 1.3 else flag.resize((W-2,H-2))
    flag = flag.pad(1, "grey")
    return Image.from_column([
      Image.from_text(d['name'], FONT(32, bold=True), beard_line=True, fg=fg),
      Image.from_text(description, FONT(24, italics=True), beard_line=True, fg=fg),
      flag
      ], padding=2, bg=bg, equal_widths=True)


grid = grid_chart(data, process, padding=(10,20), fg=fg, bg=bg, yalign=(0.5,0.5,0.5), row_label=lambda r: None if data.index[r].startswith("_") else Image.from_text(data.index[r].replace(r"\n","\n").upper(), FONT(32, bold=True), align="center"))
title = Image.from_text_justified("Some flags with 6-pointed stars".upper(), grid.width, 80, partial(FONT, bold=True), fg=fg, bg=bg, padding=20)
img = Image.from_column([title, grid, Rectangle((0,30))], bg=bg).pad((20,0), bg=bg)
img.place(Image.from_text("/u/Udzu", FONT(24), fg=fg, bg=bg, padding=5).pad((1,1,0,0), fg), align=1, padding=5, copy=False)
img.save("output/flagsstars.png")
