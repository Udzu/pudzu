from pudzu.charts import *

# TODO: 10 downwards

df = pd.read_csv("datasets/flagsgrey.csv")

FONT = sans
fg, bg="black", "#EEEEEE"
default_img = "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b0/No_flag.svg/1024px-No_flag.svg.png"

def process(d):
    if not d: return None
    description = get_non(d, 'description')
    description = "{}".format(description) if description else " "
    flag = Image.from_url_with_cache(get_non(d, 'image', default_img)).to_rgba()
    flag = flag.resize_fixed_aspect(height=198) if flag.width / flag.height < 1.3 else flag.resize((318,198))
    def t(a): return int(not any(alpha==0 for _,_,_,alpha in a))
    a = np.array(flag); padding = (t(a[:,0]), t(a[0]), t(a[:,-1]), t(a[-1]))
    flag= flag.pad(padding, "grey")
    return Image.from_column([
      Image.from_text(d['name'].replace(r'\n','\n'), FONT(28, bold=True), align="center", beard_line=True, fg=fg),
      Image.from_text(description, FONT(24, italics=True), fg=fg, beard_line=True),
      flag
      ], padding=2, bg=bg, equal_widths=True)

title = Image.from_text("Some flags with grey in them".upper(), FONT(68, bold=True), fg=fg, bg=bg, align="center").pad(30, bg).pad((0,0,0,10), bg)

groups = list(remove_duplicates(df.group))
array = [[dict(r) for _,r in df.iterrows() if r.group == g] for g in groups]
data = pd.DataFrame(array, index=groups)
grid1 = grid_chart(data, process, padding=(10,20), fg=fg, bg=bg, yalign=0, row_label=lambda r: Image.from_text("{}".format(data.index[r]).upper(), FONT(32, bold=True), align="center", line_spacing=3) if not data.index[r].startswith("_") else None).pad((10,0),bg)

img = Image.from_column([title, grid1, Rectangle((0,50))], bg=bg)
img.place(Image.from_text("/u/Udzu", FONT(24), fg=fg, bg=bg, padding=5).pad((1,1,0,0), fg), align=1, padding=5, copy=False)
img.save("output/flagsgrey.png")
