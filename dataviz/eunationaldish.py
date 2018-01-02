import sys
sys.path.append('..')
from charts import *
from PIL import ImageFilter

# generate map
df = pd.read_csv("datasets/eunationaldish.csv").set_index('country')
bg = '#181820'
fg = 'white'

def colorfn(c, w, h):
    if c == 'Sea':
        return bg
    elif c == 'Borders':
        return "#D0D0D0"
    elif c not in df.index:
        return "#B0B0B0"
    elif nnn(df.image[c]):
        return Image.from_url_with_cache(df.image[c]).crop_to_aspect(w, h).resize((w,h)).darken(0.25)
    return "grey"
    
def labelfn(c, w, h):
    if c not in df.index: return None
    x = Image.from_text_bounded(df.name[c], (w, h), 24, papply(arial, bold=True), padding=4, max_width=w, align="center", fg="white")
    y = x.replace_color("white", "black", ignore_alpha=True).filter(ImageFilter.BLUR)
    return y.place(x)
    
map = map_chart("maps/Europe.png", colorfn, labelfn, resize_patterns=True)

title = Image.from_column([
Image.from_text("National dishes of Europe".upper(), arial(52, bold=True), fg),
Image.from_markup("according to some folk on the web, so errors are //their// fault, right?", partial(arial, 28), fg)
], bg=bg)

img = Image.from_column([title, map], padding=10, bg=bg)
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg=fg, bg=bg, padding=5).pad((1,1,0,0), fg), align=1, padding=10, copy=False)
img.save("output/eunationaldishes.png")
