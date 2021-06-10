from pudzu.charts import *
from pudzu.sandbox.bamboo import *

# ----------------------
# 40 under 40 grid chart
# ----------------------

df = pd.read_csv("datasets/etymfoodeponyms.csv")
data = pd.DataFrame(list(generate_batches((dict(row) for _,row in df.iterrows()), 8)))
default_img = "https://s-media-cache-ak0.pinimg.com/736x/0d/36/e7/0d36e7a476b06333d9fe9960572b66b9.jpg"

def process(d):
    if d is None: return None
    return Image.from_column([
      Image.from_url_with_cache(get_non(d, "food", default_img)).crop_to_aspect(100, 100, (0.5, 0.2)).resize_fixed_aspect(width=160),
      Image.new("RGBA", (160,30), "black").place(Image.from_text(d['word'], arial(18, bold=True, italics=True), padding=2, fg="white", bg="black")),
      Image.from_url_with_cache(get_non(d, "portrait", default_img)).crop_to_aspect(100, 100, (0.5, 0.2)).resize_fixed_aspect(width=160),
      Image.from_text(d['name'], arial(12, bold=True), padding=(2, 5, 2, 2), fg="white", bg="black"),
      Image.from_text("{}–{}".format(d['born'], d['died']), arial(12, bold=True), padding=(2, 2, 2, 5), fg="white", bg="black"),
      Image.from_text(d['description'], font("arial", 12), padding=(2,2,2,2), fg="white", bg="black", max_width=160, align="center")
      ])

title = Image.from_column([
    Image.from_text(f"{len(df)} foods named after historical figures".upper(), arial(48, bold=True), fg="white", bg="black")
    #Image.from_text("“It is a sobering thought, for example, that when Mozart was my age, he had been dead for two years.” — Tom Lehrer", arial(24), max_width=750, fg="white", bg="black")
    ], bg="black").pad((0,25,0,35), "black")

footer = Image.from_row([
    # Image.from_text("* ages and death causes from Wikipedia.", font=arial(14), fg="white", bg="black", padding=5),
    Image.from_text("/u/Udzu", font("arial", 14), fg="white", bg="black", padding=5).pad((1,1,0,0), "white")
    ], bg="black")
      
grid = grid_chart(data, process, padding=5, bg="black", title=title, yalign=0).pad((0,0,10,0), "black")
img = Image.from_column([grid, footer], bg="black", xalign=1, padding=10)
img.save("output/etymfoodeponyms.png")
