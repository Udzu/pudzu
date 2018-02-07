import sys
sys.path.append('..')
from charts import *

df = pd.read_csv("datasets/flagspurple.csv")
groups = list(remove_duplicates(df.group))
array = [[dict(r) for _,r in df.iterrows() if r.group == g] for g in groups]
data = pd.DataFrame(array, index=list(remove_duplicates(df.group)))

FONT = calibri
fg, bg="black", "#EEEEEE"
default_img = "https://s-media-cache-ak0.pinimg.com/736x/0d/36/e7/0d36e7a476b06333d9fe9960572b66b9.jpg"

def process(d):
    if not d: return None
    description = get_non(d, 'description')
    description = "({})".format(description) if description else " "
    return Image.from_column([
      Image.from_text(d['name'], FONT(32, bold=True), fg=fg),
      Image.from_text(description, FONT(24, italics=True), fg=fg),
      Image.from_url_with_cache(get_non(d, 'image', default_img)).to_rgba().resize((318,198)).pad(1, "grey")
      ], padding=2, bg=bg)

title = Image.from_text("Some flags that contain the color Purple".upper(), FONT(80, bold=True), fg=fg, bg=bg).pad(40, bg)

grid = grid_chart(data, process, padding=(10,20), fg=fg, bg=bg, yalign=(0.5,0.5,0.5), row_label=lambda r: Image.from_text("{}\nflags".format(data.index[r]).upper(), FONT(32, bold=True), align="center", line_spacing=3))
img = Image.from_column([title, grid, Rectangle((0,40))], bg=bg)
img.place(Image.from_text("/u/Udzu", FONT(24), fg=fg, bg=bg, padding=5).pad((1,1,0,0), fg), align=1, padding=5, copy=False)
img.save("output/flagspurple.png")
