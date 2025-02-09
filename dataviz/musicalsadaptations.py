from pudzu.charts import *
from pudzu.pillar import *
from pudzu.utils import *

df = pd.read_csv("datasets/musicalsadaptations.csv")

FONT = calibri or sans
fg, bg="black", "#EEEEEE"

def process(name, img):
    image = Image.from_url_with_cache(img).to_rgba().resize((160,250))
    labeled_image = Image.from_column([
      Image.from_text_bounded(name, image.size, 32, partial(FONT, bold=True), beard_line=True, align="center", fg=fg),
      image
      ], padding=2, bg=bg, equal_widths=True)
    return image

array = [[process(d.a, d.a_img), process(d.b, d.b_img)] for _, d in df.iterrows()]
batches = list(generate_batches(array, ceil(len(array)/3)))
grids = [Image.from_array(batch, padding=5, bg=bg) for batch in batches]
grid = Image.from_row(grids, padding=20, bg=bg, yalign=0)

title = Image.from_text(f"stories with multiple musical adaptations".upper(), FONT(80, bold=True), align="center", fg=fg, bg=bg, max_width=grid.width).pad(40, bg)

img = Image.from_column([title, grid], padding=10, bg=bg)
img.convert("RGB").save("output/musicalsadaptations.jpg", quality=90)
