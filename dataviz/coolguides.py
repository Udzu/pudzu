from pudzu.charts import *
from pudzu.pillar import *
from pudzu.utils import *

df = pd.read_csv("datasets/coolguides.csv")

FONT = font_family("FreeSerif")

def process(d):
    image = Image.from_url_with_cache(d["image"]).to_rgba()
    if not any(x in d["name"] for x in ["Chicago", "Negro"]):
        image = image.crop_to_aspect(250, 300, align=(0.75 if image.width > image.height else 0.5))
    image = image.resize((600,720))
    # TODO: markup, hyphenation, font(?)
    text = Image.from_markup(get_non(d, "text", "?"), partial(FONT, 32),
                           hyphenator=language_hyphenator(), align="left", max_width=image.width)
    return Image.from_column([image, text], padding=5)

images = [process(r) for _, r in df.iterrows()]
array = list(generate_batches(images, 3))
img = Image.from_array(array, padding=20, yalign=0)

title = Image.from_text(f"A cool guide to cool guides".upper(), liberation_serif(96, bold=True), padding=10)

img = Image.from_column([title, img], bg="white", padding=15)
img.convert("RGB").save("output/coolguides.jpg", quality=85)
img.resize_fixed_aspect(scale=2/3).convert("RGB").save("output/coolguides2.jpg", quality=85)
