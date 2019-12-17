from pudzu.charts import *
from pudzu.experimental.bamboo import *

df = pd.read_csv("datasets/flagseucolonised.csv")
data = pd.DataFrame(list(generate_batches([dict(row) for _,row in df.iterrows()], 7)))
fg, bg="black", "#EEEEEE"
default_img = "https://s-media-cache-ak0.pinimg.com/736x/0d/36/e7/0d36e7a476b06333d9fe9960572b66b9.jpg"

flags = pd.read_csv("datasets/countries.csv").split_columns(('nationality', 'tld', 'country'), "|").explode('country').set_index('country')['flag']

def process(d):
    if d is None: return None
    return Image.from_column([
      Image.from_row([Image.from_url_with_cache(flags[d['country']]).resize_fixed_aspect(height=24), 
                      Image.from_text(d['country'], arial(24, bold=True), fg=fg, bg=bg),
                      ], padding=(5,5), bg=bg),
      Image.from_text(d['name'], arial(24, bold=True), fg=fg, bg=bg),
      Image.from_text(d['description'], arial(24, italics=True), fg=fg, bg=bg),
      Image.from_url_with_cache(d['flag']).resize((318 if d['country'] != "Switzerland" else 198,198)).pad((1,1,int(d['country'] != "Germany"), 1), "grey"),
      Image.from_text(d['dates'], arial(24), fg=fg, bg=bg)
      ], padding=4, bg=bg)

title = Image.from_column([
    Image.from_text("flags from European countries' subservient pasts".upper(), arial(72, bold=True), fg=fg, bg=bg),
    Image.from_text("state and civil flags from historical client states, unequal partners and occupied territories", arial(48, italics=True), fg=fg, bg=bg)
    ], bg=bg, padding=(0,5)).pad((0,0,0,20), bg=bg)

grid = grid_chart(data, process, padding=(10,20), bg=bg, yalign=0, title=title).pad(20, bg)
grid.save("output/flagseucolonised.png")
