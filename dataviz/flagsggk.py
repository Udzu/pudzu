from pudzu.charts import *

df = pd.read_csv("datasets/flagsggk.csv")
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
    flag = flag.pad((1,1,0,1) if "Devín" in d['name'] else 1, "grey")
    return Image.from_column([
      Image.from_text_bounded(d['name'].replace(r"\n","\n"), (320,200), 32, partial(FONT, bold=True), beard_line=True, fg=fg, align="center"),
      Image.from_text(description, FONT(24, italics=True), fg=fg),
      flag
      ], padding=2, bg=bg, equal_widths=True)

title = Image.from_text("Green, Gold & Black".upper(), FONT(120, bold=True), fg=fg, bg=bg).pad((40,40,40,0), bg)
subtitle = Image.from_text("eschewing the Red, White & Blue".upper(), FONT(64, italics=True), fg=fg, bg=bg).pad((0,0,0,40), bg)

grid = grid_chart(data, process, padding=(10,20), fg=fg, bg=bg, yalign=(0.5,1,0.5), row_label=lambda r: None if data.index[r].startswith("_") else Image.from_text("{}\nflags".format(data.index[r]).upper(), FONT(32, bold=True), align="center", line_spacing=3))
img = Image.from_column([title, subtitle, grid, Rectangle((0,40))], bg=bg)
img.place(Image.from_text("/u/Udzu", FONT(24), fg=fg, bg=bg, padding=5).pad((1,1,0,0), fg), align=1, padding=5, copy=False)
img.save("output/flagsggk.png")
