from pudzu.charts import *

df = pd.read_csv("datasets/flagsconlangs.csv")
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
    flag = flag.pad(0 if "coat" in d['group'] else (1,0,0,0) if "imperial" in str(d['description']) else 1, "grey")
    return Image.from_column([
      Image.from_text_bounded(d['name'].replace(r"\n","\n"), (320 if "Switzerland" not in description else 200,200), 32, partial(FONT, bold=True), beard_line=True, align="center", fg=fg),
      Image.from_text(description, FONT(24, italics=True), fg=fg),
      flag
      ], padding=2, bg=bg, equal_widths=True)


FLAG = "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f9/Conlangflag.svg/1920px-Conlangflag.svg.png"
flag = Image.from_url_with_cache(FLAG).to_rgba().resize_fixed_aspect(height=100).pad(1, "grey")

title = Image.from_text(f"conlang flags".upper(), FONT(80, bold=True), fg=fg, bg=bg).pad((0,30,0,10), bg)
subtitle = Image.from_text("(dates are of language creation, not flag adoption)", FONT(24, italics=False), fg=fg, bg=bg)
titles = Image.from_row([flag, Image.from_column([title, subtitle]), flag], padding=(20,0), yalign=1)

grid = grid_chart(data, process, padding=(10,20), fg=fg, bg=bg, yalign=(0.5,1,0.5), row_label=lambda r: None if data.index[r].startswith("_") else Image.from_text("{}".format(data.index[r].replace(r"\n","\n")).upper(), FONT(32, bold=True), align="center", line_spacing=3))
img = Image.from_column([titles, grid, Rectangle((0,50))], bg=bg)
img.place(Image.from_text("/u/Udzu", FONT(24), fg=fg, bg=bg, padding=5).pad((1,1,0,0), fg), align=1, padding=5, copy=False)
img.save("output/flagsconlangs.png")

