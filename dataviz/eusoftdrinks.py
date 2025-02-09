from pudzu.charts import *
from pudzu.sandbox.bamboo import *

FONT = sans

df = pd.read_csv("datasets/eusoftdrinks.csv")
df["pad"] = df["pad"].fillna(0)
data = pd.DataFrame(list(generate_batches((dict(row) for _,row in df.iterrows()), 8)))
default_img = "https://s-media-cache-ak0.pinimg.com/736x/0d/36/e7/0d36e7a476b06333d9fe9960572b66b9.jpg"
flags = pd.read_csv("datasets/countries.csv").split_columns('country', "|").explode('country').set_index('country').flag
flags["Scotland"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/Flag_of_Scotland.svg/1920px-Flag_of_Scotland.svg.png"
flags["England"] = "https://upload.wikimedia.org/wikipedia/en/thumb/b/be/Flag_of_England.svg/1920px-Flag_of_England.svg.png"
flags["Wales"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dc/Flag_of_Wales.svg/1920px-Flag_of_Wales.svg.png"
flags["N. Ireland"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/8/81/Saint_Patrick%27s_Saltire.svg/1920px-Saint_Patrick%27s_Saltire.svg.png"

def flag(country):
    flag = Image.from_url_with_cache(flags[country]).to_rgba()
    flag = flag.resize_fixed_aspect(height=90) if flag.width / flag.height < 1.1 else flag.resize((160, 90))
    flag = flag.trim(1).pad(1, "grey").pad((0, 10, 0, 0), "black")
    return flag

def process(d):
    if d is None: return None
    return Image.from_column([
      Image.from_text(d["country"].replace("North ","N. ").upper(), FONT(18, bold=True), fg="white"),
      flag(d["country"].strip("*")),
      Image.from_url_with_cache(get_non(d, "image", default_img)).to_rgba().pad((0,int(d["pad"])), "white").pad_to_aspect(1, bg="white").crop_to_aspect(100, 100).resize_fixed_aspect(width=160).pad((0,5), bg=None),
      Image.new("RGBA", (160,40), "black").place(Image.from_text(d['drink'].replace(r"\n","\n"), FONT(18, bold=True), padding=2, max_width=160, fg="white", align="center", bg="black")),
      ])

title = Image.from_column([
    Image.from_text(f"Soft drinks from across Europe".upper(), FONT(64, bold=True), fg="white", bg="black"),
#    Image.from_text("foods invented since World War II that feel older than they are", FONT(34, italics=True), fg="white", bg="black")
    ], bg="black", padding=5).pad((0,25,0,35), "black")

footer = Image.from_row([
#    Image.from_text("* developed in Switzerland by a German then soon moved to the UK", font=arial(16), fg="white", bg="black", padding=5),
    Image.from_text("/u/Udzu", font("arial", 16), fg="white", bg="black", padding=5).pad((1,1,0,0), "white")
    ], bg="black")
      
grid = grid_chart(data, process, padding=5, bg="black", title=title, yalign=0).pad((0,0,10,0), "black")
img = Image.from_column([grid, footer], bg="black", xalign=1, padding=10)
img.save("output/eusoftdrinks.png")
img.convert("RGB").save("output/eusoftdrinks.jpg", quality=95)

#