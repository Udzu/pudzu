from pudzu.charts import *
from pudzu.sandbox.bamboo import *

df = pd.read_csv("datasets/foodrecent.csv")
data = pd.DataFrame(list(generate_batches((dict(row) for _,row in df.iterrows()), 8)))
default_img = "https://s-media-cache-ak0.pinimg.com/736x/0d/36/e7/0d36e7a476b06333d9fe9960572b66b9.jpg"
countries = pd.read_csv("datasets/countries.csv").split_columns(('nationality', 'tld', 'country'), "|").explode('country').set_index('country')

def flag(country):
    flag = Image.from_url_with_cache(countries.flag[country]).to_rgba()
    flag = flag.resize_fixed_aspect(height=90) if flag.width / flag.height < 1.3 else flag.resize((160, 90))
    flag = flag.trim(1).pad(1, "grey").pad((0, 10, 0, 0), "black")
    return flag

def process(d):
    if d is None: return None
    return Image.from_column([
      flag(d["country"]),
      Image.from_url_with_cache(get_non(d, "image", default_img)).to_rgba().crop_to_aspect(100, 100, (0.5, 0.2)).resize_fixed_aspect(width=160).pad((0,5), bg=None),
      Image.new("RGBA", (160,40), "black").place(Image.from_text(d['food'], arial(18, bold=True), padding=2, max_width=160, fg="white", align="center", bg="black")),
      Image.from_text(d['year'], arial(16, italics=True), padding=(2, 5, 2, 2), fg="white", bg="black"),
      ])

title = Image.from_column([
    Image.from_text(f"Surprisingly recently invented foods".upper(), arial(52, bold=True), fg="white", bg="black"),
    Image.from_text("foods invented since World War II that feel older than they are", arial(34, italics=True), fg="white", bg="black")
    ], bg="black", padding=5).pad((0,25,0,35), "black")

footer = Image.from_row([
    # Image.from_text("* ages and death causes from Wikipedia.", font=arial(14), fg="white", bg="black", padding=5),
    Image.from_text("/u/Udzu", font("arial", 14), fg="white", bg="black", padding=5).pad((1,1,0,0), "white")
    ], bg="black")
      
grid = grid_chart(data, process, padding=5, bg="black", title=title, yalign=0).pad((0,0,10,0), "black")
img = Image.from_column([grid, footer], bg="black", xalign=1, padding=10)
img.save("output/foodrecent.png")
img.convert("RGB").save("output/foodrecent.jpg", quality=95)
