import sys
import seaborn as sns
sys.path.append('..')
from charts import *

countries = pd.read_csv("datasets/countries.csv").split_columns(('nationality', 'tld', 'country'), "|").split_rows('country').set_index('country')

df = pd.read_csv("datasets/eujohns.csv")
average_scores = df.groupby('country').mean().score
df = df.assign_rows(sortby=lambda r: average_scores[r.country]).sort_values(['sortby', 'score'], ascending=False).drop(['sortby'], axis=1)
dfi = df.set_index('link')

fg, bg = "white", "black"
def entitle(img, i=None):
    title = Image.from_text("The most famous historical Johns from each European country" + ("" if i is None else " [{}/3]".format(i+1)), arial(60, bold=True), fg=fg, bg=bg)
    subtitle = Image.from_text("people called John, or any of its alternate or derived forms, born between 1000–1900", arial(48), align="center", fg=fg, bg=bg)
    footer = Image.from_text("¹ pen name of Henryk Goldszmit; highest John-from-birth is Jan III Sobieski ² born in Bosnia to Croatian parents and wrote mainly in Serbian.\nfame measure is based on Wikipedia article lengths, revision counts and monthly views, averaged across different language Wikipedias.", arial(36), max_width=img.width, align="center", fg=fg, bg=bg, padding=(0, 10))
    return Image.from_column([title, subtitle, img, footer], bg=bg).pad(10,bg=bg)

grids = []
for i in range(3): 

    start = i * 15
    table = pd.DataFrame([[df.iloc[n]['link']] for n in range(start,min(len(df), start+15))], index=[df.iloc[n]['country'] for n in range(start,min(len(df), start+15))]).transpose()

    DEFAULT_IMG = "https://s-media-cache-ak0.pinimg.com/736x/0d/36/e7/0d36e7a476b06333d9fe9960572b66b9.jpg"
        
    def cell(img, name):
        box = Image.new("RGB", (180,200), bg)
        box = box.place(Image.from_column([
          img.crop_to_aspect(100, 100, (0.5, 0.2)).resize_fixed_aspect(width=160),
          Image.from_text(name, arial(12, bold=True), padding=(3, 5, 3, 2), fg=fg, bg=bg),
          Image.from_text(get_non(dfi['description'], name, ""), arial(12), padding=(3,0,3,0), fg=fg, bg=bg)
          ], bg=bg))
        return box
        
    def flag(column):
        flag = Image.from_url_with_cache(countries.flag[table.columns[column]]).resize((160,100)).pad((0,20), "black")
        return flag

    grid = grid_chart(table, lambda n: n and get_non(dfi['image'], n, DEFAULT_IMG), image_process=cell, col_label=flag, bg=bg)
    grids.append(grid)
    
chart = Image.from_column(grids, xalign=0)
entitle(chart).save("output/eujohns.jpg")    

# TODO: Azerbaijan, Kosovo, Malta
