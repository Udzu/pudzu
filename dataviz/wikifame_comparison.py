import sys
import seaborn as sns
sys.path.append('..')

from charts import *

# wikifame comparison

fg, bg = "white", "black"
DEFAULT_IMG = "https://s-media-cache-ak0.pinimg.com/736x/0d/36/e7/0d36e7a476b06333d9fe9960572b66b9.jpg"
TITLE = "the most famous person born each century"
SUBTITLE = "according to different language Wikipedias"
FOOTNOTE = "fame measure is a combination of article length, number of edits, and typical number of pageviews"

df = pd.read_csv("datasets/wikibirths_comparison.csv")
table = pd.crosstab(df.century, df.language, df.name, aggfunc=lambda i : i.iloc[0])
gb =  df.groupby(['name', 'language']).first()

def process(img, name, row, column):
    box = Image.new("RGB", (180,200), bg)
    box = box.place(Image.from_column([
      img.crop_to_aspect(100, 100, (0.5, 0.2)).resize_fixed_aspect(width=160),
      Image.from_text(name, arial(12, bold=True), padding=(3, 5, 3, 2), fg=fg, bg=bg),
      Image.from_text(get_non(gb['description'], (name, table.columns[column]), ""), arial(12), padding=(3,0,3,0), fg=fg, bg=bg)
      ], bg=bg))
    return box
    
flags = pd.read_csv("datasets/countries.csv").split_columns(('nationality', 'tld', 'country'), "|").split_rows('tld').set_index('tld')['flag']
flags[".en"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/English_language.svg/1024px-English_language.svg.png"
flags[".ja"] = flags[".jp"]
flags[".zh"] = flags[".cn"]

def language_flag(column):
    return Image.from_url_with_cache(flags[".{}".format(table.columns[column])]).resize((160,100)).pad((0,20), "black")
    
# TODO: use flag for language labels
grid = grid_chart(table, lambda n, r, c: n and get_non(gb['image_url'], (n, table.columns[c]), DEFAULT_IMG), image_process=process, row_label=arial(20, bold=True), col_label=language_flag, bg=bg)

title = Image.from_column([
Image.from_text(TITLE, arial(60, bold=True), fg=fg, bg=bg).pad((10,0), bg=bg),
Image.from_text(SUBTITLE, arial(36, bold=True), fg=fg, bg=bg).pad((10,0,10,2), bg=bg)
], bg=bg).pad((0,10),bg=bg)
comment = Image.from_text(FOOTNOTE, arial(24), fg=fg, bg=bg).pad((0,20,0,5),bg=bg)

chart = Image.from_column([title, grid, comment], bg=bg)
chart.place(Image.from_text("/u/Udzu", font("arial", 24), fg=fg, bg=bg, padding=5).pad((1,1,0,0), fg), align=1, padding=0, copy=False)

# chart.save(OUTPUT)
