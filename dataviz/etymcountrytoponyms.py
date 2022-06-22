from pudzu.charts import *
from pudzu.sandbox.bamboo import *

# ----------------------
# 40 under 40 grid chart
# ----------------------

df = pd.read_csv("datasets/etymcountrytoponyms.csv").sort_values("country")
df = df[~df.country.str.startswith("#")]
data = pd.DataFrame(list(generate_batches((dict(row) for _,row in df.iterrows()), 11)))
default_img = "https://s-media-cache-ak0.pinimg.com/736x/0d/36/e7/0d36e7a476b06333d9fe9960572b66b9.jpg"
flags = pd.read_csv("../dataviz/datasets/countries.csv").split_columns(('country'), "|").explode('country').set_index('country').flag
flags["Scotland"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/Flag_of_Scotland.svg/1920px-Flag_of_Scotland.svg.png"
flags["Wales"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dc/Flag_of_Wales.svg/1920px-Flag_of_Wales.svg.png"
flags["England"] = "https://upload.wikimedia.org/wikipedia/en/thumb/b/be/Flag_of_England.svg/1920px-Flag_of_England.svg.png"
flags["Afghanistan"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cd/Flag_of_Afghanistan_%282013%E2%80%932021%29.svg/1280px-Flag_of_Afghanistan_%282013%E2%80%932021%29.svg.png"

def half_and_half(img1, img2):
    assert img1.size == img2.size
    w, h = (wh - 1 for wh in img1.size)
    mask_array = np.fromfunction(lambda y,x: (h*x)/w >= y, tuple(reversed(img1.size)))
    mask = Image.fromarray((mask_array * 255).astype('uint8')).convert("1")
    return img2.overlay(img1, mask=mask, copy=True)

def process(d):
    if d is None: return None
    if "Australia" in d['country']:
        flag = half_and_half(Image.from_url_with_cache(flags["New Zealand"]).resize((900,600)), Image.from_url_with_cache(flags["Australia"]).resize((900,600)))
    else:
        flag = Image.from_url_with_cache(flags.get(d['country'].rstrip("*"), default_img))

    return Image.from_column([
      flag.to_rgba().resize((98 if d['country'] == "Switzerland" else 158,98)).pad(1, "grey"),
      Image.new("RGBA", (160,30), "black").place(Image.from_text(d['country'], arial(16, bold=True), padding=2, fg="white", bg="black")),
      Image.from_url_with_cache(get_non(d, "image", default_img)).crop_to_aspect(100, 100, (get_non(d, "crop", 0.5), get_non(d, "crop", 0.2))).resize_fixed_aspect(width=160),
      Image.from_markup(f"**{d['word']}**", partial(arial, 14, bold=True), padding=(2, 5, 2, 2), fg="white", bg="black"),
      Image.from_text(get_non(d, 'description'), arial(12, italics=True), padding=(2,2,2,2), fg="white", bg="black", max_width=160, align="center") if get_non(d, 'description') else None,
      ])

title = Image.from_column([
    Image.from_text(f"{len(df)} things that are named after countries".upper(), arial(48, bold=True), fg="white", bg="black")
    ], bg="black").pad((0,25,0,35), "black")

footer = Image.from_row([
    Image.from_text("* named after the wider region rather than just the modern country", font=arial(14), fg="white", bg="black", padding=5),
    Image.from_text("/u/Udzu", font("arial", 14), fg="white", bg="black", padding=5).pad((1,1,0,0), "white")
    ], bg="black")
      
grid = grid_chart(data, process, padding=5, bg="black", title=title, yalign=0).pad((0,0,10,0), "black")
img = Image.from_column([grid, footer], bg="black", xalign=1, padding=10)
img.convert("RGB").save("output/etymcountrytoponyms.png")
