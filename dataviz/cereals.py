import sys
sys.path.append('..')
from charts import *
from bamboo import *

df = pd.read_csv("datasets/cereals.csv").assign_rows(sort=lambda d: "ZZZ" if d["cereal"] == "Special K" else d["cereal"]).sort_values("sort")
data = pd.DataFrame(list(generate_batches((dict(row) for _,row in df.iterrows()), 5)))
default_img = "https://s-media-cache-ak0.pinimg.com/736x/0d/36/e7/0d36e7a476b06333d9fe9960572b66b9.jpg"
FONT = verdana
PALETTE = {"M": VegaPalette10.BLUE, "F": VegaPalette10.PINK }

def process(d):
    return Image.from_column([
      Image.new("RGBA", (180,32)).place(Image.from_text_bounded(d['cereal'], (180,32), 18, partial(FONT, bold=True), padding=2)),
      Image.from_url_with_cache(get_non(d, "image", default_img)).resize((160,240)),
      Image.from_text(d['mascot'], FONT(16, italics=True), padding=2)
      ])

grid = grid_chart(data, process, lambda d: "F" if d['cereal'] == "Special K" else "M", padding=10, yalign=0, group_rounded=True, group_padding=4, group_fg_colors=PALETTE, bg="white")

title = Image.from_text("20 breakfast cereal mascots by gender".upper(), FONT(40, bold=True))
footer = Image.from_multitext(
    ["Gender: ", Rectangle(20, PALETTE["M"]), " male ", Rectangle(20, PALETTE["F"]), " female(?)", Rectangle((150,0)), "* currently on leave     ** previously a dog"],
    [arial(16, bold=True), ..., arial(16), ..., arial(16), ..., arial(16)], img_offset=-5)
img = Image.from_column([title, grid, footer], bg="white", xalign=0.5, padding=10)
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.convert("RGB").save("output/cereals.jpg")
