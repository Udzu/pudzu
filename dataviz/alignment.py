from pudzu.charts import *
from pudzu.sandbox.bamboo import *

df = pd.read_csv("datasets/alignment_alt.csv")
default_img = "https://s-media-cache-ak0.pinimg.com/736x/0d/36/e7/0d36e7a476b06333d9fe9960572b66b9.jpg"

def a(l):
    if l == "NN":
        return "True Neutral"
    return {"L": "Lawful", "N": "Neutral", "C": "Chaotic"}[l[0]] + " " +  {"G": "Good", "E": "Evil", "N": "Neutral"}[l[1]]

def cell(r):
    img = Image.from_url_with_cache(get_non(r, "image", default_img)).convert("RGBA").crop_to_aspect(1, align=get_non(r, "align", 0.5)).resize_fixed_aspect(width=200)
    # label = Image.from_text(r.label, sans(16, bold=True), RGBA(0,0,0,80))
    # img = img.place(label, align=(0.5,1), padding=5)
    img = img.pad(10, "white").pad(1, "black")
    alignment = Image.from_text(a(r.alignment).upper(), sans(16, bold=True), "#333333")
    return Image.from_column([alignment, img], padding=2)

imgs = list(generate_batches([cell(r) for _,r in df.iterrows()], 3))
imgs = [list(l) for l in imgs]
img = Image.from_array(imgs, padding=2, bg="white")

title = Image.from_text("ALT ALIGNMENT CHART", sans(56, bold=True))
img = Image.from_column([title, img], padding=5, bg="white")
img.save("output/alignment_alt.png")