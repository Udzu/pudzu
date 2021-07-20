from pudzu.charts import *

df = pd.read_csv("datasets/flagsnewold.csv")
groups = list(remove_duplicates(df.group))
array = [[dict(r) for _,r in df.iterrows() if r.group == g] for g in groups]

COLS = 3
arrays = list(generate_batches(array, ceil(len(array) / COLS)))
datas = [pd.DataFrame(array) for array in arrays]

FONT = calibri or sans
fg, bg="black", "#EEEEEE"
default_img = "https://s-media-cache-ak0.pinimg.com/736x/0d/36/e7/0d36e7a476b06333d9fe9960572b66b9.jpg"

def process(d):
    if not d: return None
    description = get_non(d, 'description')
    description = "({})".format(description) if description else " "
    if get_non(d, 'image'):
        flag = Image.from_url_with_cache(get_non(d, 'image', default_img)).to_rgba()
        flag = flag.resize_fixed_aspect(height=198) if flag.width / flag.height < 1.3 else flag.resize((318,198))
        flag = flag.pad(0 if "coat" in d['group'] else (1,1,0,1) if "Venice" in d['name'] else 1, "grey")
    else:
        flag = Rectangle((320,200), bg)
    return Image.from_column([
      Image.from_text_bounded(d['name'].replace(r"\n","\n"), (320,200), 32, partial(FONT, bold=True), beard_line=True, align="center", fg=fg),
      Image.from_text(description, FONT(24, italics=True), fg=fg),
      flag
      ], padding=2, bg=bg, equal_widths=True)

title = Image.from_text(f"'New' flags versus 'old'".upper(), FONT(180, bold=True), fg=fg, bg=bg).pad(40, bg)
footer = Image.from_text("""¹ New Mexico's name actually predates that of Mexico the country!     ² New Caledonia's flag is widespread but unofficial; the official flag is the French Tricolore.     ³ Unrelated to Zealand in Denmark""", FONT(40), fg=fg, bg=bg).pad(20, bg)

grids = [grid_chart(data, process, padding=(10,20), fg=fg, bg=bg, yalign=(0.5,1,0.5)) for data in datas]
grid = Image.from_row(grids, padding=(60,0), bg=bg, yalign=0)


img = Image.from_column([title, grid, footer], bg=bg)
#img.place(Image.from_text("/u/Udzu", FONT(24), fg=fg, bg=bg, padding=5).pad((1,1,0,0), fg), align=1, padding=5, copy=False)
img.save("output/flagsnewold.png")

