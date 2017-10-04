import sys
import seaborn as sns
sys.path.append('..')
from charts import *

countries = pd.read_csv("datasets/countries.csv").split_columns(('nationality', 'tld', 'country'), "|").split_rows('country').set_index('country')

df = pd.read_csv("datasets/eufame.csv")
average_scores = df.groupby('country').mean().score
df = df.assign_rows(sortby=lambda r: average_scores[r.country]).sort_values(['sortby', 'score'], ascending=False).drop(['sortby'], axis=1)
dfi = df.set_index('link')

grids = []
for i in [1]: # range(3): 

    start = i * 15
    table = pd.DataFrame([[df.iloc[n*5+i]['link'] for i in range(5)] for n in range(start,start+15)], index=[df.iloc[n*5]['country'] for n in range(start,start+15)]).transpose()

    DEFAULT_IMG = "https://s-media-cache-ak0.pinimg.com/736x/0d/36/e7/0d36e7a476b06333d9fe9960572b66b9.jpg"
    fg, bg = "white", "black"

    def cell(img, name):
        box = Image.new("RGB", (180,200), bg)
        box = box.place(Image.from_column([
          img.crop_to_aspect(100, 100, (0.5, 0.2)).resize_fixed_aspect(width=160),
          Image.from_text(name, arial(12, bold=True), padding=(3, 5, 3, 2), fg=fg, bg=bg),
          Image.from_text(get_non(dfi['description'], name, ""), arial(12), padding=(3,0,3,0), fg=fg, bg=bg)
          ], bg=bg))
        return box
        
    def flag(column):
        return Image.from_url_with_cache(countries.flag[table.columns[column]]).resize((160,100)).pad((0,20), "black")

    grid = grid_chart(table, lambda n: n and get_non(dfi['image'], n, DEFAULT_IMG), image_process=cell, col_label=flag, bg=bg)
    grid.save("output/eufame{}.jpg".format(i))
    grids.append(grid)
    
# chart = Image.from_column(grids)
# chart.save("output/eufame.jpg")    


