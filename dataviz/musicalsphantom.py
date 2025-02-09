from pudzu.charts import *
from pudzu.pillar import *
from pudzu.utils import *

df = pd.read_csv("datasets/musicalsphantom.csv")

FONT = calibri or sans
fg, bg="black", "#EEEEEE"

def process(year, name, img):
    image = Image.from_url_with_cache(img).to_rgba().resize((160,250))
    labeled_image = Image.from_column([
      image,
      Image.from_text(f"{name} ({year})", FONT(16, bold=True), beard_line=True, max_width=image.width, align="center", fg=fg),
      ], padding=2, bg=bg, equal_widths=True)
    return labeled_image

array = [process(d.year, d["name"], d.image) for _, d in df.iterrows()]
batches = list(generate_batches(array, 5))
grid = Image.from_array(batches, padding=20, bg=bg, yalign=0)

title = Image.from_text(f"{len(df)} musical adaptations of\nThe Phantom of the Opera".upper(), FONT(48, bold=True), align="center", fg=fg, bg=bg, max_width=grid.width).pad(40, bg)

img = Image.from_column([title, grid], padding=10, bg=bg)
img.convert("RGB").save("output/musicalsadaptations.jpg", quality=90)
