from pudzu.charts import *

df = pd.read_csv("datasets/flagsrussia.csv")
array = [dict(r) for _,r in df.iterrows()]
array[25:25] = [None]*2
array[87:87] = [None]*3
array = list(generate_batches(array, 9))
data = pd.DataFrame(array)
PALETTE = [c.brighten(0.3) for c in VegaPalette10]

FONT = calibri
fg, bg="black", "#EEEEEE"
default_img = "https://s-media-cache-ak0.pinimg.com/736x/0d/36/e7/0d36e7a476b06333d9fe9960572b66b9.jpg"

def process(d):
    if not d: return None
    flag = Image.from_url_with_cache(get_non(d, 'flag', default_img)).to_rgba()
    flag = flag.resize_fixed_aspect(height=198) if flag.width / flag.height < 1.3 else flag.resize((318,198))
    flag = flag.pad(1, "grey")
    return Image.from_column([
      Image.from_text(d['name'], FONT(32, bold=True), beard_line=True, fg=fg, max_width=318, align="center"),
      flag
      ], padding=2, equal_widths=True).pad((4,0,4,12), None)

def group(d):
    return d and d.get('type')
    
title = Image.from_text("Flags of the Federal Subjects of Russia".upper(), FONT(120, bold=True), fg=fg, bg=bg).pad(40, bg)

grid = grid_chart(data, process, group, padding=(10,10), fg=fg, bg=bg, yalign=1, xalign=0.5,
    group_rounded=True, group_padding=5, group_fg_colors=PALETTE)
    
footer = Image.from_multitext(
    ["Type: ", Rectangle(40, PALETTE[0]), " republic ",
               Rectangle(40, PALETTE[1]), " federal city ", 
               Rectangle(40, PALETTE[2]), " krai ", 
               Rectangle(40, PALETTE[3]), " oblast ", 
               Rectangle(40, PALETTE[4]), " autonomous oblast ", 
               Rectangle(40, PALETTE[5]), " autonomous okrug ", 
               Rectangle(40, PALETTE[6]), " former subject ", 
               Rectangle((100,0)),
               "*not recognized internationally"],
    [arial(44, bold=True), ..., arial(44), 
                           ..., arial(44),
                           ..., arial(44),
                           ..., arial(44),
                           ..., arial(44),
                           ..., arial(44),
                           ..., arial(44),
                           ..., arial(44, italics=True)], img_offset=-5, bgs=bg).pad((10,20), bg)
    
img = Image.from_column([title, grid, footer], bg=bg, padding=(20,0))
img.place(Image.from_text("/u/Udzu", FONT(24), fg=fg, bg=bg, padding=5).pad((1,1,0,0), fg), align=1, padding=5, copy=False)
img.save("output/flagsrussia.png")
