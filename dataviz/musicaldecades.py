from pudzu.charts import *
from pudzu.pillar import *
from pudzu.utils import *

df = pd.read_csv("datasets/musicaldecades.csv")
groups = list(remove_duplicates(y // 10 for y in df.year))
array = [[dict(r) for _,r in df.iterrows() if r.year // 10 == g] for g in groups]
data = pd.DataFrame(array, index=[f"{g}0s" for g in groups])[:-2]
assert len(data) == 8

FONT = calibri or sans
fg, bg="black", "#EEEEEE"
default_img = "https://s-media-cache-ak0.pinimg.com/736x/0d/36/e7/0d36e7a476b06333d9fe9960572b66b9.jpg"

def process(d):
    if not d: return None
    image = Image.from_url_with_cache(get_non(d, 'image', default_img)).to_rgba()
    if "Oliver" in d["name"]: image = image.trim((0,0,15,15))
    elif "Silver Lake" in d["name"]: image = image.trim((0,0,10,20))
    elif "Lady" in d["name"]: image = image.trim((0,0,12,12))
    image = image.resize((160,250))
    # labeled_image = Image.from_column([
    #   Image.from_text_bounded(d['name'].replace(r"\n","\n"), image.size, 32, partial(FONT, bold=True), beard_line=True, align="center", fg=fg),
    #   image
    #   ], padding=2, bg=bg, equal_widths=True)
    return image

def label(r, df, *args, **kwargs):
    label = strip_from(df.index[r], "_")
    return Rectangle((300,250), bg).place(Image.from_text(label, FONT(48, bold=True)))

title = Image.from_text(f"favourite musicals from each decade".upper(), FONT(80, bold=True), fg=fg, bg=bg).pad(40, bg)

grid1 = grid_chart(data[:len(data)//2], process, padding=(0,0), fg=fg, bg=bg, yalign=(0.5,1,0.5), row_label=partial(label, df=data[:len(data)//2]))
grid2 = grid_chart(data[len(data)//2:], process, padding=(0,0), fg=fg, bg=bg, yalign=(0.5,1,0.5), row_label=partial(label, df=data[len(data)//2:]))
img = Image.from_column([title, Image.from_row([grid1, grid2], padding=20), Rectangle((0,0))], bg=bg)
# img.place(Image.from_text("/u/Udzu", FONT(24), fg=fg, bg=bg, padding=5).pad((1,1,0,0), fg), align=1, padding=5, copy=False)
# img.save("output/musicaldecades.png")
img.convert("RGB").save("output/musicaldecades.jpg", quality=90)
