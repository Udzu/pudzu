import sys
import seaborn as sns
sys.path.append('..')
from charts import *

countries = pd.read_csv("datasets/countries.csv").split_columns(('nationality', 'tld', 'country'), "|").split_rows('country').set_index('country')

df = pd.read_csv("datasets/eufame.csv")
average_scores = df.groupby('country').mean().score
df = df.assign_rows(sortby=lambda r: average_scores[r.country]).sort_values(['sortby', 'score'], ascending=False).drop(['sortby'], axis=1)
dfi = df.set_index('link')

fg, bg = "white", "black"
def entitle(img, i=None):
    title = Image.from_text("The most famous historical figures born in each European country between 1000–1900" + ("" if i is None else " [{}/3]".format(i+1)), arial(60, bold=True), fg=fg, bg=bg)
    subtitle = Image.from_text("fame based on Wikipedia¹; countries² based on birthplace and modern borders, NOT nationality", arial(48), align="center", fg=fg, bg=bg)
    footer = Image.from_text("¹ fame measure is a combination of Wikipedia article length, number of revisions and monthly views; scores averaged across English, French, German, Spanish, Russian, Chinese and Japanese Wikipedias. ² omits European microstates and dependencies; countries are ordered by average score of top 5 individuals.", arial(36), max_width=img.width, fg=fg, bg=bg, padding=(0, 10))
    return Image.from_column([title, subtitle, img, footer], bg=bg).pad(10,bg=bg)

grids = []
for i in range(3): 

    start = i * 15
    table = pd.DataFrame([[df.iloc[n*5+i]['link'] for i in range(5)] for n in range(start,start+15)], index=[df.iloc[n*5]['country'] for n in range(start,start+15)]).transpose()

    DEFAULT_IMG = "https://s-media-cache-ak0.pinimg.com/736x/0d/36/e7/0d36e7a476b06333d9fe9960572b66b9.jpg"
        
    def cell(name):
        if not name: return None
        img = Image.from_url_with_cache(get_non(dfi['image'], n, DEFAULT_IMG))
        box = Image.new("RGB", (180,200), bg)
        box = box.place(Image.from_column([
          img.crop_to_aspect(100, 100, (0.5, 0.2)).resize_fixed_aspect(width=160),
          Image.from_text(name, arial(12, bold=True), padding=(3, 5, 3, 2), fg=fg, bg=bg),
          Image.from_text(get_non(dfi['description'], name, ""), arial(12), padding=(3,0,3,0), fg=fg, bg=bg)
          ], bg=bg))
        return box
        
    def flag(column):
        return Image.from_url_with_cache(countries.flag[table.columns[column]]).resize((160,100)).pad((0,20), "black")

    grid = grid_chart(table, cell, col_label=flag, bg=bg)
    entitle(grid, i=i).save("output/wikifame_eu{}.jpg".format(i))
    grids.append(grid)
    
chart = Image.from_column(grids)
entitle(chart).save("output/wikifame_eu.jpg")    


