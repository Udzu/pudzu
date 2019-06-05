from pudzu.charts import *

# https://people.wku.edu/charles.smith/music/images/stats6.pdf

countries = pd.read_csv("datasets/countries.csv").split_columns(('nationality', 'tld', 'country'), "|").split_rows('country').set_index('country')

df = pd.read_csv("datasets/eucomposerstop.csv")
dfi = df.set_index('link')
dfc = df.set_index('country')

fg, bg = "white", "black"
def entitle(img):
    title = Image.from_text("Most influential European classical composers by country".upper(), arial(64, bold=True), fg=fg, bg=bg)
    subtitle = Image.from_text("(from Top 500 Composers list by The Classical Music Navigator, based on a combination of 11 variables)", arial(48), align="center", fg=fg, bg=bg)
    return Image.from_column([title, subtitle, img], bg=bg).pad(20,bg=bg)

grids = []
for i in [0, 1]: 

    start = i * 14
    cs = remove_duplicates(df.country)[start:start + 14]
    table = pd.DataFrame([list(make_iterable(dfc.link[c])) for c in cs], index=cs).transpose()

    DEFAULT_IMG = "https://s-media-cache-ak0.pinimg.com/736x/0d/36/e7/0d36e7a476b06333d9fe9960572b66b9.jpg"
        
    def cell(name):
        if not name: return None
        img = Image.from_url_with_cache(get_non(dfi['image'], name, DEFAULT_IMG))
        box = Image.new("RGB", (180,210), bg)
        box = box.place(Image.from_column([
          img.crop_to_aspect(100, 100, (0.5, 0.2)).resize_fixed_aspect(width=160),
          Image.from_text("#{}".format(dfi["rank"][name]), arial(16, bold=True), padding=(3, 5, 3, 0), fg=fg, bg=bg),
          Image.from_text(name, arial(14, bold=False), padding=(3, 5, 3, 5), fg=fg, bg=bg)
          ], bg=bg))
        return box
        
    def flag(column):
        country = table.columns[column]
        return Image.from_url_with_cache(countries.flag[country]).to_rgba().resize((100 if country == "Switzerland" else 160,100)).pad(1, "grey").pad((0,20), "black")

    grid = grid_chart(table, cell, col_label=flag, bg=bg)
    grids.append(grid)
    
chart = Image.from_column(grids, xalign=0)
img = entitle(chart).convert("RGB")
img.place(Image.from_text("/u/Udzu", font("arial", 24), fg=fg, bg=bg, padding=5).pad((1,1,0,0), fg), align=1, padding=0, copy=False)
img.save("output/eucomposers.jpg")    


