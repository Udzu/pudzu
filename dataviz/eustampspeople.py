import seaborn as sns
from pudzu.charts import *

FONT, fg, bg = sans, "white", "black"

countries = pd.read_csv("datasets/countries.csv").split_columns(('nationality', 'tld', 'country'), "|").explode('country').set_index('country')
flags = countries.flag
flags["Czechoslovakia"] = flags["Czech Republic"]
flags["USSR"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a9/Flag_of_the_Soviet_Union.svg/1024px-Flag_of_the_Soviet_Union.svg.png"
flags["Yugoslavia"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e5/Flag_of_Yugoslavia_%281918%E2%80%931941%29.svg/1024px-Flag_of_Yugoslavia_%281918%E2%80%931941%29.svg.png"
df = pd.read_csv("datasets/eustampspeople.csv")

def entitle(img):
    title = Image.from_text("First historical figures on European stamps".upper(), FONT(96, bold=True), fg=fg, bg=bg)
    subtitle = Image.from_text("(excluding early religious figures and living royals or politicians)", FONT(72), fg=fg, bg=bg).pad((0,0,0,10), bg)
    img = Image.from_column([title, subtitle, img], bg=bg, padding=5).pad(15,bg=bg)
    img = img.place(Image.from_text("/u/Udzu", FONT(16), fg=fg, bg=bg, padding=5).pad((1,1,0,0), fg), align=1, padding=10)
    return img

grids = []
rows = 4
for row in generate_batches(df.iterrows(), ceil(len(df)/rows)):

    table = pd.DataFrame([[dict(d) for _,d in row]], columns=[d.country for _,d in row])
    DEFAULT_IMG = "https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Solid_black.svg/480px-Solid_black.svg.png"
        
    def cell(d):
        if not d: return None
        elif not get_non(d, 'country'): 
            return Image.from_text(str(d['name']).upper(), FONT(24, bold=True), fg=fg, bg=bg, line_spacing=5, beard_line=True, max_width=320, padding=(30,10), align="center")
        logger.info(d['country'])
        stamp = Image.from_url_with_cache(get_non(d, 'image', DEFAULT_IMG))
        if stamp.width > stamp.height * 1.33: stamp = stamp.transpose(Image.ROTATE_270)
        stamp = stamp.resize_fixed_aspect(width=160)
        return Image.from_column([
          stamp,
          Image.from_text(d['name'], FONT(16, bold=True),fg=fg, bg=bg, line_spacing=5, beard_line=True, max_width=160, align="center"),
          Image.from_row(
            ([] if get_non(d, 'alt_flag') is None else [Image.from_url_with_cache(d['alt_flag']).to_rgba().resize((25,15)).pad(1, "grey")]) +
            [Image.from_text(str(get_non(d, 'date', '')), FONT(16, bold=True), fg=fg, bg=bg, beard_line=True)],
            padding=3),
          Image.from_text(d['description'], FONT(16, italics=True),fg=fg, bg=bg, line_spacing=5, beard_line=True, max_width=160, align="center")
          ], bg=bg, padding=2).pad(5, bg)
        
    def flag(column):
        if non(table.columns[column]): return None
        flag = Image.from_url_with_cache(countries.flag[table.columns[column].rstrip("*").split(" (")[0]]).to_rgba()
        flag = flag.resize_fixed_aspect(height=100) if flag.width / flag.height < 1.3 else flag.resize((160,100))
        flag = flag.trim(1).pad(1, "grey").pad((0,10,0,0), bg)
        label = Image.from_text(table.columns[column].upper(), FONT(20, bold=True),fg=fg,bg=bg,beard_line=True)
        return Image.from_column([label, flag.pad((0,0,0,10),bg=bg)])

    grid = grid_chart(table, cell, col_label=flag, bg=bg, yalign=0)
    grids.append(grid)
    
chart = Image.from_column(grids, xalign=0, padding=5)
chart = entitle(chart)
chart.convert("RGB").save("output/eustampspeople.jpg")

