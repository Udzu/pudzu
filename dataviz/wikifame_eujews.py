import sys
import seaborn as sns
sys.path.append('..')
from charts import *

FONT, fg, bg = calibri, "white", "black"

countries = pd.read_csv("datasets/countries.csv").split_columns(('nationality', 'tld', 'country'), "|").split_rows('country').set_index('country')
df = pd.read_csv("datasets/eujews.csv")

def entitle(img):
    title = Image.from_text("Famous Europeans of Jewish origin ".upper(), FONT(96, bold=True), fg=fg, bg=bg)
    subtitle = Image.from_text("(roughly ordered by how famous they are)", FONT(72), fg=fg, bg=bg).pad((0,0,0,10), bg)
    footer = Image.from_text("Missing countries: Montenegro, Andorra, Faroe Islands and Vatican City.", FONT(36), fg=fg, bg=bg)
    return Image.from_column([title, subtitle, img, footer], bg=bg, padding=5).pad(15,bg=bg)

grids = []
for row in generate_batches(df.iterrows(), ceil(len(df)/4)):

    table = pd.DataFrame([[dict(d) for _,d in row]], columns=[d.country for _,d in row])
    DEFAULT_IMG = "https://s-media-cache-ak0.pinimg.com/736x/0d/36/e7/0d36e7a476b06333d9fe9960572b66b9.jpg"
        
    def cell(d):
        if not d: return None
        return Image.from_column([
          Image.from_url_with_cache(get_non(d, 'image', DEFAULT_IMG)).cropped_resize((160,160), (0.5,get_non(d, 'align', 0.2))),
          Image.from_text(d['link'], FONT(16, bold=True), fg=fg, bg=bg),
          Image.from_text(d['description'], FONT(16, italics=True),fg=fg, bg=bg)
          ], bg=bg, padding=2).pad(10, bg)
        
    def flag(column):
        flag = Image.from_url_with_cache(countries.flag[table.columns[column]]).to_rgba()
        flag = flag.resize_fixed_aspect(height=100) if flag.width / flag.height < 1.3 else flag.resize((160,100))
        flag = flag.trim(1).pad(1, "grey")
        return flag

    grid = grid_chart(table, cell, col_label=flag, bg=bg)
    grids.append(grid)
    
chart = Image.from_column(grids, xalign=0)
chart = entitle(chart)

