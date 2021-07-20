from pudzu.charts import *

df = pd.read_csv("datasets/flagsnaked.csv")
groups = list(remove_duplicates(df.group))
array = [[dict(r) for _,r in df.iterrows() if r.group == g] for g in groups]
data = pd.DataFrame(array, index=list(remove_duplicates(df.group)))

FONT = calibri or sans
fg, bg="black", "#EEEEEE"
default_img = "https://s-media-cache-ak0.pinimg.com/736x/0d/36/e7/0d36e7a476b06333d9fe9960572b66b9.jpg"

N = 2

def process(d):
    if not d: return None
    description = get_non(d, 'description')
    description = "({})".format(description) if description else " "
    flag = Image.from_url_with_cache(get_non(d, 'image', default_img)).to_rgba()
    flag = flag.resize_fixed_aspect(height=N*198) if flag.width / flag.height < 1.3 else flag.resize((318*N,198*N))
    flag = flag.pad(N, "grey")
    return Image.from_column([
      Image.from_text_bounded(d['name'].replace(r"\n","\n"), (320*N,200*N), 32*N, partial(FONT, bold=True), beard_line=True, align="center", fg=fg),
      Image.from_text(description, FONT(24*N, italics=True), fg=fg),
      flag
      ], padding=2*N, bg=bg, equal_widths=True)

title = Image.from_text("Bare chests on flags".upper(), FONT(80*N, bold=True), fg=fg, bg=bg).pad(40*N, bg)

grid = grid_chart(data, process, padding=(10*N,20*N), fg=fg, bg=bg, yalign=(0.5,0.5,0.5), row_label=lambda r: None if data.index[r].startswith("_") else Image.from_text(data.index[r].replace(r"\n","\n").upper(), FONT(32*N, bold=True), align="center"))
img = Image.from_column([title, grid, Rectangle((0,40*N))], bg=bg)
img.place(Image.from_text("/u/Udzu", FONT(24*N), fg=fg, bg=bg, padding=5*N).pad((N,N,0,0), fg), align=1, padding=5*N, copy=False)
img.save("output/flagsnaked.png")
