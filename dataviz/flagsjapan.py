from pudzu.charts import *

COLS = 7
N = 1

df = pd.read_csv("datasets/flagsjapan.csv")
array = list(generate_batches([dict(r) for _,r in df.iterrows()], COLS))
data = pd.DataFrame(array)

FONT = sans
fg, bg="black", "#EEEEEE"
default_img = "https://s-media-cache-ak0.pinimg.com/736x/0d/36/e7/0d36e7a476b06333d9fe9960572b66b9.jpg"

def process(d):
    if not d or d["name"] == "_": return None
    description = get_non(d, 'etymology', '')
    flag = Image.from_url_with_cache(get_non(d, 'flag', default_img)).to_rgba()
    flag = flag.resize_fixed_aspect(height=N*198) if flag.width / flag.height < 1.3 else flag.resize((N*318,N*198))
    flag = flag.pad(N, "grey")
    return Image.from_column([
      Image.from_text_bounded(d['name'].replace(r"\n","\n"), (N*320 if "Switzerland" not in description else N*200,N*200), N*32, partial(FONT, bold=True), beard_line=True, align="center", fg=fg),
      Image.from_text_bounded(description, (N*320 if "Switzerland" not in description else N*200,N*200), N*24, partial(FONT, italics=True), align="center", fg=fg),
      flag
      ], padding=N*2, bg=bg, equal_widths=True)

title = Image.from_text(f"Japanese prefecture flag meanings".upper(), FONT(N*96, bold=True), fg=fg, bg=bg).pad(N*40, bg)

grid = grid_chart(data, process, padding=(N*10,N*20), fg=fg, bg=bg, yalign=(0.5,1,0.5))
img = Image.from_column([title, grid, Rectangle((0,N*50))], bg=bg)
img.place(Image.from_text("/u/Udzu", FONT(N*24), fg=fg, bg=bg, padding=5).pad((N*1,N*1,0,0), fg), align=1, padding=N*5, copy=False)
img.save("output/flagsjapan.png")

