import sys
import seaborn as sns
sys.path.append('..')

from charts import *

# wikifame birth grids


SPECS = [["datasets/wikibirths.csv", "output/wikibirths.jpg",
          "100 famous people from the second millennium", "the most famous person born each decade, according to English Wikipedia",
          "{}00s", "'{}0s", range(10,20), range(0,10)],
         ["datasets/wikibirths_dead.csv", "output/wikibirths_dead.jpg",
          "100 historical figures from the second millennium", "the most famous historical figure born each decade, according to English Wikipedia",
          "{}00s", "'{}0s", range(10,20), range(0,10)],          
         ["datasets/wikibirths_20c.csv", "output/wikibirths_20c.jpg",
          "100 famous people from the 20th century", "the most famous person born each year, according to English Wikipedia",
          "19{}0s", "'{}", range(0,10), range(0,10)],
         ["datasets/wikibirths_f.csv", "output/wikibirths_f.jpg",
          "100 famous women from the second millennium", "the most famous woman born each decade, according to English Wikipedia",
          "{}00s", "'{}0s", range(10,20), range(0,10)],
         ["datasets/wikibirths_global.csv", "output/wikibirths_global.jpg",
          "famous people from the second millennium", "the most famous person born each decade, according to Wikipedia",
          "{}00s", "'{}0s", range(10,19), range(0,10)]
          ]
          
# FOOTNOTE = "*fame measure is a combination of article length, number of edits, and typical number of pageviews"
# FOOTNOTE = "restricted to people who died at least 20 years ago; fame measure is a combination of article length, number of edits, and typical number of pageviews"
FOOTNOTE = "based on English, French, German, Spanish, Russian, Chinese and Japanese Wikipedias; fame is a combination of article length, number of edits, and pageviews"

for DATASET, OUTPUT, TITLE, SUBTITLE, ROWFORMAT, COLFORMAT, ROWRANGE, COLRANGE in SPECS[-1:]:

    fg, bg = "white", "black"
    DEFAULT_IMG = "https://s-media-cache-ak0.pinimg.com/736x/0d/36/e7/0d36e7a476b06333d9fe9960572b66b9.jpg"

    df = pd.read_csv(DATASET)
    table = pd.DataFrame([[df.iloc[century*10+decade]['name'] if century*10+decade < len(df) else None for decade in range(0,len(COLRANGE))] for century in range(0,len(ROWRANGE))],
                         index=[ROWFORMAT.format(c) for c in ROWRANGE], columns=[COLFORMAT.format(d) for d in COLRANGE])
    df = df.set_index('name')

    if "description" not in df: df = df.assign_rows(description="")
    if "image_url" not in df: df = df.assign_rows(image_url=None)

    def process(img, name):
        box = Image.new("RGB", (180,200), bg)
        box = box.place(Image.from_column([
          img.crop_to_aspect(100, 100, (0.5, 0.2)).resize_fixed_aspect(width=160),
          Image.from_text(name, arial(12, bold=True), padding=(3, 5, 3, 2), fg=fg, bg=bg),
          Image.from_text(get_non(df['description'], name, ""), arial(12), padding=(3,0,3,0), fg=fg, bg=bg)
          ], bg=bg))
        return box
        
    grid = grid_chart(table, lambda n: n and get_non(df['image_url'], n, DEFAULT_IMG), image_process=process, row_label=arial(20, bold=True), col_label=arial(20, bold=True), bg=bg)
    
    title = Image.from_column([
    Image.from_text(TITLE, arial(60, bold=True), fg=fg, bg=bg).pad((10,0), bg=bg),
    Image.from_text(SUBTITLE, arial(36, bold=True), fg=fg, bg=bg).pad((10,0,10,2), bg=bg)
    ], bg=bg).pad((0,10),bg=bg)
    comment = Image.from_text(FOOTNOTE, arial(24), fg=fg, bg=bg).pad((0,20,0,5),bg=bg)

    chart = Image.from_column([title, grid, comment], bg=bg)
    chart.place(Image.from_text("/u/Udzu", font("arial", 24), fg=fg, bg=bg, padding=5).pad((1,1,0,0), fg), align=1, padding=0, copy=False)

    chart.save(OUTPUT)
