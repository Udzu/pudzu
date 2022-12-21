from pudzu.charts import *
from pudzu.sandbox.bamboo import *

df = pd.read_csv("datasets/cognomens.csv")
data = pd.DataFrame(list(generate_batches((dict(row) for _,row in df.iterrows()), 9)))
default_img = "https://s-media-cache-ak0.pinimg.com/736x/0d/36/e7/0d36e7a476b06333d9fe9960572b66b9.jpg"

def process(d):

    if d is None: return None
    return Image.from_column([
      Image.from_url_with_cache(get_non(d, "image", default_img)).to_rgba().crop_to_aspect(100, 100, (0.5, 0.2)).resize_fixed_aspect(width=160).pad((0,5), bg=None),
      Image.new("RGBA", (160,40), "black").place(Image.from_text(d['name'], arial(18, bold=True), padding=2, max_width=160, fg="white", align="center", bg="black")),
      Image.from_text(f"({d['years']})".replace("-","–"), arial(14), padding=(2, 5, 2, 2), fg="white", bg="black"),
      Image.from_text(d['description'], arial(16, italics=True), padding=(2, 5, 2, 2), fg="white", bg="black"),
      ])

title = Image.from_column([
    Image.from_text(f"a selection of historical royal cognomens".upper(), arial(52, bold=True), fg="white", bg="black"),
    Image.from_text("nicknames attached to the monarchs' names, either during or after their lifetime", arial(34, italics=True), fg="white", bg="black")
    ], bg="black", padding=5).pad((0,25,0,35), "black")

footer = Image.from_row([
    Image.from_markup("¹ also known as William the Bastard   ² //Séamus an Chaca// in Irish  ", font_family=partial(arial, 14), fg="white", bg="black", padding=5),
    Image.from_text("/u/Udzu", font("arial", 14), fg="white", bg="black", padding=5).pad((1,1,0,0), "white")
    ], bg="black")
      
grid = grid_chart(data, process, padding=5, bg="black", title=title, yalign=0).pad((0,0,10,0), "black")
img = Image.from_column([grid, footer], bg="black", xalign=1, padding=10)
img.convert("RGB").save("output/cognomens.jpg", quality=95)

# Historical royal cognomens, from Charles the Fat to Henry the Impotent
