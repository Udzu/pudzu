import seaborn as sns
from pudzu.charts import *

FONT, fg, bg = calibri, "white", "black"

countries = pd.read_csv("datasets/countries.csv").split_columns(('nationality', 'tld', 'country'), "|").split_rows('country').set_index('country')
df = pd.read_csv("datasets/euamericans.csv")

def entitle(img):
    title = Image.from_text("First generation European-Americans ".upper(), FONT(96, bold=True), fg=fg, bg=bg)
    subtitle = Image.from_text("(migrants and children of migrants, in rough order of fame)", FONT(72), fg=fg, bg=bg).pad((0,0,0,10), bg)
    img = Image.from_column([title, subtitle, img], bg=bg, padding=5).pad(15,bg=bg)
    img = img.place(Image.from_text("/u/Udzu", FONT(16), fg=fg, bg=bg, padding=5).pad((1,1,0,0), fg), align=1, padding=10)
    return img

grids = []
for row in generate_batches(df.iterrows(), ceil(len(df)/4)):

    table = pd.DataFrame([[dict(d) for _,d in row]], columns=[d.country for _,d in row])
    DEFAULT_IMG = "https://s-media-cache-ak0.pinimg.com/736x/0d/36/e7/0d36e7a476b06333d9fe9960572b66b9.jpg"
        
    def cell(d):
        if not d: return None
        logger.info(d['name'])
        return Image.from_column([
          Image.from_url_with_cache(get_non(d, 'image', DEFAULT_IMG)).cropped_resize((160,160), (0.5,get_non(d, 'align', 0.2))),
          Image.from_text(d['name'], FONT(16, bold=True), fg=fg, bg=bg, beard_line=True),
          Image.from_text(d['description'], FONT(16, italics=True),fg=fg, bg=bg, beard_line=True),
          Image.from_text("({})".format(d['comment']) if nnn(d['comment']) else "", FONT(16, italics=True),fg=fg, bg=bg, beard_line=True)
          ], bg=bg, padding=2).pad(5, bg)
        
    def flag(column):
        flag = Image.from_url_with_cache(countries.flag[table.columns[column]]).to_rgba()
        flag = flag.resize_fixed_aspect(height=100) if flag.width / flag.height < 1.3 else flag.resize((160,100))
        flag = flag.trim(1).pad(1, "grey").pad((0,10,0,0), bg)
        label = Image.from_text(table.columns[column].upper(), FONT(20, bold=True),fg=fg,bg=bg,beard_line=True)
        return Image.from_column([flag.pad((0,0,0,10),bg=bg), label])

    grid = grid_chart(table, cell, col_label=flag, bg=bg)
    grids.append(grid)
    
chart = Image.from_column(grids, xalign=0)
chart = entitle(chart)
chart.convert("RGB").save("output/wikifame_euus.jpg")

