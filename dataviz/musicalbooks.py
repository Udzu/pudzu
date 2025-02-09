from pudzu.charts import *
from pudzu.pillar import *
from pudzu.utils import *

df = pd.read_csv("datasets/musicalbooks.csv")

def process(d):
    default_img = "https://s-media-cache-ak0.pinimg.com/736x/0d/36/e7/0d36e7a476b06333d9fe9960572b66b9.jpg"
    image = Image.from_url_with_cache(get_non(d, 'image', default_img)).to_rgba()
    image = image.resize((200,300))
    description = f"{d['name']} ({d['year']})"
    return Image.from_column([
        image,
#        Image.from_text(description, sans(16, bold=True), align="center", max_width=200, padding=(0,5))
    ], equal_widths=True)
    return image

images = [process(r) for _, r in df.iterrows()]
array = list(generate_batches(images, 10))
img = Image.from_array(array, yalign=0, padding=(0,0))

title = Image.from_text(f"{len(df)} books that were adapted into musicals".upper(), sans(60, bold=True), padding=10)

img = Image.from_column([title, img], bg="white", padding=10)
img.convert("RGB").save("output/musicalbooks.jpg", quality=85)
