from pudzu.charts import *
from pudzu.pillar import *
from pudzu.utils import *

imgs = []
for s in ["", "2"]:
    df = pd.read_csv(f"datasets/musicalyears{s}.csv").set_index("year")
    start = 197 if s else 192
    array = [[df.T.get(10*d+y) for y in range(10)] for d in range(start,203)]
    data = pd.DataFrame(array, index=[f"{g}x" for g in range(start,203)])
    data = data.sort_index(ascending=False)

    FONT = calibri or sans
    fg, bg="black", "#EEEEEE"
    default_img = "https://upload.wikimedia.org/wikipedia/commons/thumb/7/75/Flag_of_None_%28square%29.svg/768px-Flag_of_None_%28square%29.svg.png"

    W = 150

    def process(d, r, c):
        if r==0 and c >= 5: return None
        url = default_img if d is None else d.get("image", default_img)
        image = Image.from_url_with_cache(url).to_rgba()
        image = image.resize((W,W))
        return image

    def label(r):
        return Rectangle((W,W), bg).place(Image.from_text(data.index[r], FONT(28, bold=True)))

    def clabel(c):
        return Rectangle((W,W//2), bg).place(Image.from_text(str(c), FONT(28, bold=True)))

    TITLE = "50 years, 50 more musicals" if s else "100 years, 100 musicals"
    SUBTITLE = "my second favourite musical from each year in the past half century"  if s else "my favourite musical from each year in the past century"
    title = Image.from_text(TITLE.upper(), FONT(76, bold=True))
    subtitle = Image.from_text(SUBTITLE, FONT(40, italics=True))

    grid = grid_chart(data, process, padding=(0,0), fg=fg, bg=bg, yalign=(0.5,1,0.5), row_label=label, col_label=clabel)
    img = Image.from_column([title, subtitle, grid, Rectangle((0,0))], bg=bg, padding=5)
    # img.place(Image.from_text("/u/Udzu", FONT(24), fg=fg, bg=bg, padding=5).pad((1,1,0,0), fg), align=1, padding=5, copy=False)
    # img.save("output/musicaldecades.png")
    imgs.append(img)
    img.convert("RGB").save(f"output/musicalyears{s}.jpg", quality=90)

Image.from_column(imgs, padding=(0,20), bg=bg).convert("RGB").save(f"output/musicalyears12.jpg", quality=90)