import seaborn as sns
from pudzu.charts import *
from pudzu.sandbox.bamboo import *

FONT, fg, bg = sans, "white", "black"

countries = pd.read_csv("datasets/countries.csv").split_columns(('nationality', 'tld', 'country'), "|").explode('country').set_index('country')
flags = countries.flag
df = pd.read_csv("datasets/stampsinflation.csv")
flags["Serbia & Montenegro"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3e/Flag_of_Serbia_and_Montenegro_%281992%E2%80%932006%29.svg/1920px-Flag_of_Serbia_and_Montenegro_%281992%E2%80%932006%29.svg.png"
flags["Russia"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e5/Flag_of_the_Russian_Soviet_Federative_Socialist_Republic_%281918%E2%80%931925%29.svg/1920px-Flag_of_the_Russian_Soviet_Federative_Socialist_Republic_%281918%E2%80%931925%29.svg.png"
flags["Greece"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6e/Flag_of_Greece_%281822-1978%29.svg/1280px-Flag_of_Greece_%281822-1978%29.svg.png"
flags["Bosnia & Herzegovina"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/3/35/Flag_of_Bosnia_and_Herzegovina_%281992%E2%80%931998%29.svg/1920px-Flag_of_Bosnia_and_Herzegovina_%281992%E2%80%931998%29.svg.png"
flags["Hungary"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f2/Flag_of_Hungary_%281946-1949%2C_1956-1957%3B_1-2_aspect_ratio%29.svg/1920px-Flag_of_Hungary_%281946-1949%2C_1956-1957%3B_1-2_aspect_ratio%29.svg.png"

def row(r):
    flag = Image.from_url_with_cache(flags[r.country]).to_rgba()
    flag = flag.resize_fixed_aspect(height=100) if flag.width / flag.height < 1.3 else flag.resize((160, 100))
    flag = flag.trim(2).pad(2, "grey").pad((0, 10, 0, 0), bg)
    flag = Image.from_column([flag, Image.from_text(f"{r.country}, {r.year}".replace("& ","& \n"), FONT(22, bold=True), fg="white", align="center")], padding=5)

    return [
        flag,
        Image.from_url_with_cache(r.image).pad_to_aspect(200,160).resize_fixed_aspect(width=200),
        Image.from_text(r.facevalue, FONT(32, bold=True), fg="white", padding=(20,0)),
    ]

stamps = Image.from_array([row(r) for _,r in df.iterrows()], padding=5, bg="black", xalign=(0.5,0.5,0))

title = Image.from_text("hyperinflation issues".upper(), FONT(64, bold=True), fg=fg, bg=bg)
subtitle = Image.from_text("highest denomination European stamps", FONT(36), fg=fg, bg=bg)

img = Image.from_column([title, subtitle, stamps], bg=bg, padding=5).pad(15, bg=bg)
img = img.place(
    Image.from_text("/u/Udzu", FONT(16), fg=fg, bg=bg, padding=5).pad((1, 1, 0, 0), fg), align=1,
    padding=10)

img.save("output/stampsinflation.png")