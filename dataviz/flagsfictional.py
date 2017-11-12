import sys
sys.path.append('..')
from charts import *
from bamboo import *

df = pd.read_csv("datasets/flagsfictional.csv")
data = pd.DataFrame(list(generate_batches([dict(row) for _,row in df.iterrows()], 3)))
fg, bg="black", "white"
default_img = "https://s-media-cache-ak0.pinimg.com/736x/0d/36/e7/0d36e7a476b06333d9fe9960572b66b9.jpg"

galactic_color = sorted(Image.from_url_with_cache(df.filter_rows("place ~ Galactic").iloc[0].flag).convert("RGBA").getcolors(65536), reverse=True)[0][1]

def process(d):
    return Image.from_column([
      Image.from_text(d['source'], arial(24, bold=True), fg=fg, bg=bg),
      Image.from_text(d['place'], arial(24, italics=True), max_width=320, align="center", fg=fg, bg=bg, padding=(0,0,0,4)),
      (Image.from_url_with_cache(d['flag']).resize((318,201)).crop((0,0,318,198)) if "Zamunda"  in d['place'] else
       Image.from_url_with_cache(d['flag']).resize((318,198)) if "Galactic" not in d['place'] else
       Image.from_url_with_cache(printed(d['flag'])).resize_fixed_aspect(height=198).crop_to_aspect(1).pad_to_aspect(318,198,bg=galactic_color)).pad(1, "grey"),
      Image.from_url_with_cache(get_non(d, 'image', default_img)).crop_to_aspect(320,200).resize((320,200))
      ], padding=4, bg=bg)

title = Image.from_column([
    Image.from_text("Fictional flags from film & TV", arial(72, bold=True), fg=fg, bg=bg),
    Image.from_text(" ", arial(48, italics=True), fg=fg, bg=bg)
    ], bg=bg)
      
grid = grid_chart(data, process, padding=(10,20), bg=bg, yalign=0, title=title).pad(20, bg)
grid.save("output/flagsfictional.png")
