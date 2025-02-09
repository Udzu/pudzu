from pudzu.charts import *
from pudzu.sandbox.bamboo import *
from pudzu.pillar import *

arial = sans

# ----------------------
# 40 under 40 grid chart
# ----------------------

df = pd.read_csv("datasets/etymcountrymisnomers.csv")
df = df[~df.country.str.startswith("#")]
data = pd.DataFrame(list(generate_batches((dict(row) for _,row in df.iterrows()), 9)))
default_img = "https://s-media-cache-ak0.pinimg.com/736x/0d/36/e7/0d36e7a476b06333d9fe9960572b66b9.jpg"
flags = pd.read_csv("../dataviz/datasets/countries.csv").split_columns(('country'), "|").explode('country').set_index('country').flag
flags["Hawaii"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ef/Flag_of_Hawaii.svg/1920px-Flag_of_Hawaii.svg.png"
flags["Wales"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dc/Flag_of_Wales.svg/1920px-Flag_of_Wales.svg.png"
flags["England"] = "https://upload.wikimedia.org/wikipedia/en/thumb/b/be/Flag_of_England.svg/1920px-Flag_of_England.svg.png"
flags["Scotland"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/Flag_of_Scotland.svg/1920px-Flag_of_Scotland.svg.png"
flags["Salisbury"] = "https://upload.wikimedia.org/wikipedia/commons/7/7f/SalisburyCathedral-wyrdlight-EastExt.jpg"
flags["London"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Flag_of_the_City_of_London_%282x1%29.svg/1920px-Flag_of_the_City_of_London_%282x1%29.svg.png"

def half_and_half(img1, img2):
    assert img1.size == img2.size
    w, h = (wh - 1 for wh in img1.size)
    mask_array = np.fromfunction(lambda y,x: (h*x)/w >= y, tuple(reversed(img1.size)))
    mask = Image.fromarray((mask_array * 255).astype('uint8')).convert("1")
    return img2.overlay(img1, mask=mask, copy=True)

def process(d):
    if d is None: return None
    flag1 = Image.from_url_with_cache(flags[d['country'].rstrip("*")])
    flag2 = Image.from_url_with_cache(flags[d['actual'].rstrip("*")])

    label = get_non(d, 'description', default=f"invented in {'the ' if d['actual'] == 'USA' else ''}{d['actual']}")
    return Image.from_column([
      flag1.to_rgba().resize((88 if d['country'] == "Switzerland" else 158,88)).pad(1, "grey"),
      Image.new("RGBA", (160,40), "black").place(Image.from_text(d['word'].replace(r"\n","\n"), arial(16, bold=True), padding=2, align="center", fg="white", bg="black")),
      Image.from_url_with_cache(get_non(d, "image", default_img)).crop_to_aspect(100, 100, (get_non(d, "crop", 0.5), get_non(d, "crop", 0.2))).resize_fixed_aspect(width=160),
      Rectangle(5, "black"),
      flag2.to_rgba().resize((88 if d['actual'] == "Switzerland" else 158,88)).pad(1, "grey"),
      Image.from_text(label, arial(12, italics=False), padding=(0,4), fg="white", bg="black", max_width=160, line_spacing=3, align="center"),
      ])

title = Image.from_column([
    Image.from_text(f"culinary misnomers".upper(), arial(64, bold=True), fg="white", bg="black"),
    Image.from_text("foods that don't come from where they say they do", arial(36, italics=True), fg="white", bg="black")
    ], bg="black", padding=5).pad((0,20,0,30), "black")

footer = Image.from_row([
#    Image.from_text("* named after the wider region rather than just the modern country", font=arial(14), fg="white", bg="black", padding=5),
    Image.from_text("/u/Udzu", font("arial", 14), fg="white", bg="black", padding=5).pad((1,1,0,0), "white")
    ], bg="black")
      
grid = grid_chart(data, process, padding=5, bg="black", title=title, yalign=0).pad((0,0,10,0), "black")
img = Image.from_column([grid, footer], bg="black", xalign=1, padding=10)
img.convert("RGB").save("output/etymcountrymisnomers.jpg")
