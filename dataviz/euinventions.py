import seaborn as sns
from pudzu.charts import *
from pudzu.sandbox.bamboo import *

FONT, fg, bg = sans, "white", "black"

countries = pd.read_csv("datasets/countries.csv").split_columns(('nationality', 'tld', 'country'), "|").explode('country').set_index('country')
df = pd.read_csv("datasets/euinventions.csv")

def entitle(img):
    title = Image.from_text("Selected European inventions".upper(), FONT(96, bold=True), fg=fg, bg=bg)
    subtitle = Image.from_text("(by the nationality of the inventors)", FONT(72), fg=fg, bg=bg).pad((0,0,0,10), bg)
    footer = Image.from_text("* Tesla was an ethnic Serb born in present day Croatia, then part the Austrian Empire.", FONT(18), "white", padding=10)
    img = Image.from_column([title, subtitle, img, footer], bg=bg, padding=5).pad(15,bg=bg)
    img = img.place(Image.from_text("/u/Udzu", FONT(16), fg=fg, bg=bg, padding=5).pad((1,1,0,0), fg), align=1, padding=10)
    return img

def half_and_half(img1, img2):
    assert img1.size == img2.size
    w, h = (wh - 1 for wh in img1.size)
    mask_array = np.fromfunction(lambda y,x: h-(h*x)/w >= y, tuple(reversed(img1.size)))
    mask = Image.fromarray((mask_array * 255).astype('uint8')).convert("1")
    return img2.overlay(img1, mask=mask, copy=True)

grids = []
for row in generate_batches(df.iterrows(), ceil(len(df)/3)):

    table = pd.DataFrame([[dict(d) for _,d in row]], columns=[d.country for _,d in row])
    DEFAULT_IMG = "https://s-media-cache-ak0.pinimg.com/736x/0d/36/e7/0d36e7a476b06333d9fe9960572b66b9.jpg"
        
    def cell(d):
        if not d: return None
        logger.info(f"{d['invention']} / {d['country']}")
        return Image.from_column([
          Image.from_url_with_cache(get_non(d, 'image', DEFAULT_IMG)).cropped_resize((200,200), (0.5,get_non(d, 'align', 0.5))),
          Image.from_text(get_non(d, 'invention', '').title(), FONT(16, bold=True), fg=fg, bg=bg, beard_line=True),
          Image.from_text(get_non(d, 'inventor', ''), FONT(16, italics=True),fg=fg, bg=bg, beard_line=True),
          Image.from_text("({})".format(d['year']) if nnn(d['year']) else "", FONT(16, italics=True),fg=fg, bg=bg, beard_line=True)
          ], bg=bg, padding=2).pad(5, bg)
        
    def flag(column):
        if table.columns[column] == "Croerbia*":
            flag = half_and_half(Image.from_url_with_cache(countries.flag["Croatia"]).resize((900,600)), Image.from_url_with_cache(countries.flag["Serbia"]).resize((900,600)))
        elif table.columns[column] == "Serbatia*":
            flag = half_and_half(Image.from_url_with_cache(countries.flag["Serbia"]).resize((900,600)), Image.from_url_with_cache(countries.flag["Croatia"]).resize((900,600)))
        else:
            flag = Image.from_url_with_cache(countries.flag[table.columns[column]]).to_rgba()
        flag = flag.resize_fixed_aspect(height=140) if flag.width / flag.height < 1.3 else flag.resize((200,140))
        flag = flag.trim(1).pad(1, "grey").pad((0,10,0,0), bg)
        label = Image.from_text(table.columns[column].upper(), FONT(20, bold=True),fg=fg,bg=bg,beard_line=True)
        return Image.from_column([flag.pad((0,0,0,10),bg=bg), label])

    grid = grid_chart(table, cell, col_label=flag, bg=bg)
    grids.append(grid)
    
chart = Image.from_column(grids, xalign=0)
chart = entitle(chart)
chart.convert("RGB").save("output/euinventions.jpg")

