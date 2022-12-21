from pudzu.charts import *
from pudzu.sandbox.bamboo import *

df = pd.read_csv("datasets/cousinmarriage.csv")
data = pd.DataFrame(list(generate_batches((dict(row) for _,row in df.iterrows()), 9)))
default_img = "https://s-media-cache-ak0.pinimg.com/736x/0d/36/e7/0d36e7a476b06333d9fe9960572b66b9.jpg"

def process(d):

    if d is None: return None
    return Image.from_column([
      Image.from_url_with_cache(get_non(d, "image", default_img)).to_rgba().crop_to_aspect(100, 100, (0.5, 0.2)).resize_fixed_aspect(width=160).pad((0,5), bg=None),
      Image.new("RGBA", (160,40), "black").place(Image.from_text(f"{d['name']} ({d['years']})".replace(r"\n","\n"), arial(18, bold=True), padding=2, max_width=160, fg="white", align="center", bg="black")),
      Image.from_text(f"{d['description']}".replace("-","–"), arial(14, italics=True), padding=(2, 5, 2, 2), fg="white", bg="black"),
      Image.from_markup(f"to **{d['partner']}**", partial(arial, 14), padding=(2, 5, 2, 2), fg="white", bg="black"),
      ])

title = Image.from_column([
    Image.from_text(f"Famous people who married their first cousin".upper(), arial(52, bold=True), fg="white", bg="black"),
    Image.from_text("though its prevalence in the West has declined significantly sice the late 19th century, first-cousin marriage is still reasonably common worldwide and remains legal in the vast majority of countries",
                    arial(28, italics=True), fg="white", bg="black", max_width=1350)
    ], bg="black", padding=5).pad((0,25,0,35), "black")

footer = Image.from_row([
    Image.from_markup("¹ double first cousins  ", font_family=partial(arial, 14), fg="white", bg="black", padding=5),
    Image.from_text("/u/Udzu", font("arial", 14), fg="white", bg="black", padding=5).pad((1,1,0,0), "white")
    ], bg="black")

grid = grid_chart(data, process, padding=5, bg="black", yalign=0, title=title).pad((0,0,10,0), "black")

img = Image.from_column([grid, footer], bg="black", xalign=1, padding=10)
img.convert("RGB").save("output/cousinmarriage.jpg", quality=95)

# Historical royal cognomens, from Charles the Fat to Henry the Impotent
