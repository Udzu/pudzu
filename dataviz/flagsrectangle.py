from pudzu.charts import *

df = pd.read_csv("datasets/flagsrectangle.csv")
groups = list(remove_duplicates(df.group))
array = [[dict(r) for _,r in df.iterrows() if r.group == g] for g in groups]
data = pd.DataFrame(array, index=list(remove_duplicates(df.group)))

FONT = sans
fg, bg= "black", "#EEEEEE"
default_img = "https://s-media-cache-ak0.pinimg.com/736x/0d/36/e7/0d36e7a476b06333d9fe9960572b66b9.jpg"

def process(d):
    if not d: return None
    description = get_non(d, 'description')
    description = "({})".format(description) if description else " "
    flag = Image.from_url_with_cache(get_non(d, 'image', default_img)).to_rgba()
    flag = flag.resize_fixed_aspect(height=198) if flag.width / flag.height < 1.3 else flag.resize((318,198))
    # flag = flag.pad(1 if "Carnaro" not in d["name"] else (1,1,1,0), "grey") 
    return Image.from_column([
      Image.from_text(d['name'].replace(r'\n','\n'), FONT(24, bold=True), align="center", beard_line=True, fg=fg),
      Image.from_text(description, FONT(20, italics=True), fg=fg),
      flag
      ], padding=2, bg=bg, equal_widths=True)

title = Image.from_text("Some non-rectangular flags".upper(), FONT(60, bold=True), fg=fg, bg=bg).pad(30, bg)

grid = grid_chart(data, process, padding=(10,20), fg=fg, bg=bg, yalign=1, row_label=lambda r: Image.from_text("{}".format(data.index[r]).upper(), FONT(32, bold=True), align="center", line_spacing=3) if not data.index[r].startswith("_") else None).pad((10,0),bg)
img = Image.from_column([title, grid, Rectangle((0,50))], bg=bg)
img.place(Image.from_text("/u/Udzu", FONT(24), fg=fg, bg=bg, padding=5).pad((1,1,0,0), fg), align=1, padding=5, copy=False)
img.save("output/flagsrectangle.png")
