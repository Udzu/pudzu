import sys
sys.path.append('..')
from charts import *
from bamboo import *

# ----------------------
# 40 under 40 grid chart
# ----------------------

df = pd.read_csv("datasets/40under40.csv")
categories = remove_duplicates(df['category'])
data = pd.DataFrame([[dict(row) for _,row in df[df['category'] == cat].iterrows()] for cat in categories], index=categories)
default_img = "https://s-media-cache-ak0.pinimg.com/736x/0d/36/e7/0d36e7a476b06333d9fe9960572b66b9.jpg"

def process(d):
    return Image.from_column([
      Image.from_url_with_cache(d.get("image_url", default_img)).crop_to_aspect(100, 100, (0.5, 0.2)).resize_fixed_aspect(width=160),
      Image.from_text(d['name'], arial(12, bold=True), padding=(2, 5, 2, 0), fg="white", bg="black"),
      Image.from_text("{}, {}".format(d['age'], d['cause']), font("arial", 12), padding=(2,1,2,0), fg="white", bg="black")
      ])

title = Image.from_column([
    Image.from_text("40 under 40: historic figures who died young", arial(48, bold=True), fg="white", bg="black"),
    Image.from_text("“It is a sobering thought, for example, that when Mozart was my age, he had been dead for two years.” — Tom Lehrer", arial(24), max_width=750, fg="white", bg="black")
    ], bg="black").pad((0,25), "black")

footer = Image.from_row([
    Image.from_text("* ages and death causes from Wikipedia.", font=arial(14), fg="white", bg="black", padding=5),
    Image.from_text("/u/Udzu", font("arial", 14), fg="white", bg="black", padding=5).pad((1,1,0,0), "white")
    ], bg="black")
      
grid = grid_chart(data, process, padding=5, col_label=None, label_font=arial(20, bold=True), bg="black", title=title).pad((0,0,10,0), "black")
img = Image.from_column([grid, footer], bg="black", xalign=1, padding=5)
img.save("output/40under40.png")
