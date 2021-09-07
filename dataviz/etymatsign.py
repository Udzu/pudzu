from pudzu.charts import *
from pudzu.sandbox.bamboo import *

flags = pd.read_csv("datasets/countries.csv").split_columns('country', "|").explode('country').set_index("country").flag

flags["Catalonia"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/c/ce/Flag_of_Catalonia.svg/1280px-Flag_of_Catalonia.svg.png"

df = pd.read_csv("datasets/etymatsign.csv")
data = pd.DataFrame(list(generate_batches((dict(row) for _,row in df.iterrows()), 4)))
default_img = "https://s-media-cache-ak0.pinimg.com/736x/0d/36/e7/0d36e7a476b06333d9fe9960572b66b9.jpg"

def process(d):
    if d is None: return None
    return Image.from_column([
      Image.from_url_with_cache(get_non(flags, d["flag"], default_img)).to_rgba().resize((158,98)).pad(1, "grey"),
      Image.new("RGBA", (160,40), "black").place(Image.from_text_bounded(d['thing'].upper(), (160,40), 20, partial(arial, bold=True, italics=True), fg="white", bg="black")),
      Image.from_url_with_cache(get_non(d, "image", default_img)).crop_to_aspect(100, 100, (0.5, 0.2)).resize_fixed_aspect(width=160),
      Image.from_text(d['language'], sans(14, bold=True), padding=(0,5,0,0), fg="white", bg="black", max_width=158, align="center"),
      Image.from_text(d['description'].replace(r"\n","\n"), sans(14, italics=True), padding=(0,5,0,10), fg="white", bg="black", max_width=158, align="center")
      ])

title = Image.from_column([
    Image.from_text(f"things that the @ sign is named\nafter in different languages".upper(), arial(36, bold=True), fg="white", bg="black", align="center", line_spacing=10)
    #Image.from_text("“It is a sobering thought, for example, that when Mozart was my age, he had been dead for two years.” — Tom Lehrer", arial(24), max_width=750, fg="white", bg="black")
    ], bg="black").pad((0,25,0,35), "black")

footer = Image.from_row([
    # Image.from_text("* ages and death causes from Wikipedia.", font=arial(14), fg="white", bg="black", padding=5),
    Image.from_text("/u/Udzu", font("arial", 14), fg="white", bg="black", padding=5).pad((1,1,0,0), "white")
    ], bg="black")
      
grid = grid_chart(data, process, padding=5, bg="black", title=title, yalign=0).pad((0,0,0,0), "black")
img = Image.from_column([grid, footer], bg="black", xalign=1, padding=10)
img.save("output/etymatsign.png")
