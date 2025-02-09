import seaborn as sns
from pudzu.charts import *
from pudzu.sandbox.bamboo import *

FONT, fg, bg = sans, "white", "black"

countries = pd.read_csv("datasets/countries.csv").split_columns(('nationality', 'tld', 'country'), "|").explode('country').set_index('country')
flags = countries.flag
df = pd.read_csv("datasets/lgbtstamps.csv")

def entitle(img):
    title = Image.from_text("LGBT pride themed postage stamps".upper(), FONT(120, bold=True), fg=fg, bg=bg, padding=(0,10,0,30))
    footer = Image.from_text("* joint issue with Switzerland.", FONT(24), "white", padding=10)
    img = Image.from_column([title, img], bg=bg, padding=5).pad(15,bg=bg)
    img = img.place(Image.from_text("/u/Udzu", FONT(32), fg=fg, bg=bg, padding=10).pad((2,2,0,0), fg), align=1, padding=20)
    return img

grids = []
rows = 2
for row in generate_batches(df.iterrows(), ceil(len(df)/rows)):

    table = pd.DataFrame([[dict(d) for _,d in row]], columns=[d.country for _,d in row])
    DEFAULT_IMG = "https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Solid_black.svg/480px-Solid_black.svg.png"
        
    def cell(d):
        if not d: return None
        elif not get_non(d, 'country'): 
            return Image.from_text(str(d['name']).upper(), FONT(24, bold=True), fg=fg, bg=bg, line_spacing=5, beard_line=True, max_width=320, padding=(30,10), align="center")
        logger.info(d['country'])
        stamp = Image.from_url_with_cache(get_non(d, 'stamp', DEFAULT_IMG))
#        if stamp.width > stamp.height * 1.33: stamp = stamp.transpose(Image.ROTATE_270)
        stamp = stamp.resize_fixed_aspect(width=320)
        return Image.from_column([
          stamp,
          Image.from_text(str(get_non(d, 'description', '').replace(r"\n","\n")), FONT(24, italics=True), fg=fg, bg=bg, beard_line=True, line_spacing=2, align="center"),
          ], bg=bg, padding=4).pad(10, bg).pad((0, 0, 0, 10), bg)
        
    def flag(column):
        if non(table.columns[column]): return None
        flag = Image.from_url_with_cache(countries.flag[table.columns[column].rstrip("*").split(" (")[0]]).to_rgba()
        flag = flag.resize_fixed_aspect(height=200) if flag.width / flag.height < 1.3 else flag.resize((320,200))
        flag = flag.trim(2).pad(2, "grey").pad((0,10,0,0), bg)
        label = Image.from_text(table.columns[column].upper(), FONT(28, bold=True),fg=fg,bg=bg,beard_line=True)
        label2 = Image.from_text(str(table[table.columns[column]][0]['year']), FONT(28, bold=True),fg=fg,bg=bg,beard_line=True)
        return Image.from_column([label2, label, flag.pad((0,0,0,10),bg=bg)])

    grid = grid_chart(table, cell, col_label=flag, bg=bg, yalign=0)
    grids.append(grid)
    
chart = Image.from_column(grids, xalign=0, padding=5)
chart = entitle(chart)
chart.convert("RGB").save("output/lgbtstamps.jpg")

