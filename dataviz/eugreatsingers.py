from pudzu.charts import *
from PIL import ImageFilter

# generate map
df = pd.read_csv("datasets/eugreatsingers.csv").set_index('country')

def colorfn(c, w, h):
    if c == 'Sea':
        return '#ffffff'
    elif c == 'Borders':
        return "#D0D0D0"
    elif c not in df.index:
        return "#B0B0B0"
    elif nnn(df.image[c]):
        return Image.from_url_with_cache(df.image[c]).crop_to_aspect(w, h)
    return "grey"
    
def labelfn(c, w, h):
    if c not in df.index:
        return None
    x = Image.from_text_bounded(df.name[c], (w, h), 18, papply(arial, bold=True), padding=4, max_width=w, align="center", fg="black")
    y = x.replace_color("black", "white", ignore_alpha=True).filter(ImageFilter.BLUR)
    return y.place(x)
    
map = map_chart("maps/Europe.png", colorfn, labelfn, resize_patterns=True)

title = Image.from_column([
Image.from_text("Europe’s ‘greatest’ singers".upper(), arial(52, bold=True)),
Image.from_text("according to national spin-offs of the 100 Greatest Britons TV show", arial(28))
], bg="white")
footer = Image.from_text("* excluding Bourvil (who is best known as a comic actor) and Daniel Küblböck & Azis (who had just appeared on DSDS and Eurovision)", arial(16))
img = Image.from_column([title, map, footer], padding=10, bg="white")
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/eugreatsingers.png")
