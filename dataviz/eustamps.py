import seaborn as sns
from pudzu.charts import *

FONT, fg, bg = calibri, "white", "black"

countries = pd.read_csv("datasets/countries.csv").split_columns(('nationality', 'tld', 'country'), "|").explode('country').set_index('country')
df = pd.read_csv("datasets/eustamps.csv")

countries.flag["Zurich"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Flag_of_Canton_of_Z%C3%BCrich.svg/599px-Flag_of_Canton_of_Z%C3%BCrich.svg.png"
countries.flag["Bavaria"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/1/16/Flag_of_Bavaria_%28striped%29.svg/1024px-Flag_of_Bavaria_%28striped%29.svg.png"
countries.flag["Sardinia"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0d/Flag_of_Italy_%281861-1946%29_crowned.svg/640px-Flag_of_Italy_%281861-1946%29_crowned.svg.png"
countries.flag["Ionian Islands"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a6/Flag_of_the_United_States_of_the_Ionian_Islands.svg/1024px-Flag_of_the_United_States_of_the_Ionian_Islands.svg.png"

def entitle(img):
    title = Image.from_text("Victoria to Teresa: Europe's first stamps".upper(), FONT(96, bold=True), fg=fg, bg=bg)
    subtitle = Image.from_text("(first definitive issues of each country, excluding overprints)", FONT(72), fg=fg, bg=bg).pad((0,0,0,10), bg)
    img = Image.from_column([title, subtitle, img], bg=bg, padding=5).pad(15,bg=bg)
    img = img.place(Image.from_text("/u/Udzu", FONT(16), fg=fg, bg=bg, padding=5).pad((1,1,0,0), fg), align=1, padding=10)
    return img

grids = []
rows = 5
for row in generate_batches(df.iterrows(), ceil(len(df)/rows)):

    table = pd.DataFrame([[dict(d) for _,d in row]], columns=[d.country for _,d in row])
    DEFAULT_IMG = "https://s-media-cache-ak0.pinimg.com/736x/0d/36/e7/0d36e7a476b06333d9fe9960572b66b9.jpg"
        
    def cell(d):
        if not d: return None
        elif not get_non(d, 'country'): 
            return Image.from_text(str(d['date']).upper(), FONT(24, bold=True), fg=fg, bg=bg, line_spacing=5, beard_line=True, max_width=320, padding=(30,10), align="center")
        logger.info(d['country'])
        return Image.from_column([
          Image.from_url_with_cache(get_non(d, 'image', DEFAULT_IMG)).resize_fixed_aspect(width=160),
          Image.from_row(
            ([] if get_non(d, 'alt_flag') is None else [Image.from_url_with_cache(d['alt_flag']).to_rgba().resize((25,15)).pad(1, "grey")]) +
            [Image.from_text(str(d['date']), FONT(16, bold=True), fg=fg, bg=bg, beard_line=True)],
            padding=3),
          Image.from_text(d['description'], FONT(16, italics=True),fg=fg, bg=bg, line_spacing=5, beard_line=True, max_width=160, align="center")
          ], bg=bg, padding=2).pad(5, bg)
        
    def flag(column):
        if non(table.columns[column]): return None
        flag = Image.from_url_with_cache(countries.flag[table.columns[column].rstrip("*")]).to_rgba()
        flag = flag.resize_fixed_aspect(height=100) if flag.width / flag.height < 1.3 else flag.resize((160,100))
        flag = flag.trim(1).pad(1, "grey").pad((0,10,0,0), bg)
        label = Image.from_text(table.columns[column].upper(), FONT(20, bold=True),fg=fg,bg=bg,beard_line=True)
        return Image.from_column([label, flag.pad((0,0,0,10),bg=bg)])

    grid = grid_chart(table, cell, col_label=flag, bg=bg, yalign=0)
    grids.append(grid)
    
chart = Image.from_column(grids, xalign=0, padding=5)
chart = entitle(chart)
chart.convert("RGB").save("output/eustamps.jpg")

