import sys
sys.path.append('..')
from charts import *
from bamboo import *
import seaborn as sns

# generate map
df = pd.read_csv("datasets/eumonarchies.csv").set_index('country')

republics = ImageColor.from_floats(sns.color_palette("Blues", 4))
monarchies = RGBA(204,85,85,255)
never = RGBA(207,215,225,255)

def stripe(c1, c2):
    return Image.from_column([Image.new("RGBA", (100,3), c1), Image.new("RGBA", (100,2), c2)])

def colorfn(c):
    abolished = ValueCache()
    if c not in df.index:
        return None if c == 'Sea' else "grey"
    elif df['monarchy'][c]:
        col = monarchies
    elif none_or_nan(df['abolished'][c]):
        col = never
    elif abolished.set(int(re.search('[0-9]+', df['abolished'][c]).group())) < 1914:
        col = republics[1]
    elif abolished.value < 1939:
        col = republics[2]
    else:
        col = republics[3]
    if c in ['Serbia', 'Croatia', 'Slovenia', 'Bosnia', 'Macedonia', 'Montenegro', 'Kosovo']:
        col = stripe(col, republics[3])
    return col
    
map = map_chart("maps/Europe.png", colorfn, ignoring_exceptions(lambda c: str(get_non(df.loc[c], "abolished", ""))), label_font=arial(16, bold=True))

# generate legend
font_size = 16
def box(c, box_size=30): return Image.new("RGBA", (box_size, box_size), c)
def stripebox(c1, c2, box_size=30): return Image.from_pattern(stripe(c1, c2), (box_size,box_size))

year_arr = Image.from_array([
[box(monarchies), Image.from_text("Still a monarchy", arial(font_size), padding=(10,0))],
[box(republics[3]), Image.from_text("Post-1939", arial(font_size), padding=(10,0))],
[box(republics[2]), Image.from_text("Post-1914", arial(font_size), padding=(10,0))],
[box(republics[1]), Image.from_text("Pre-1914", arial(font_size), padding=(10,0))],
[box(never), Image.from_text("Never a monarchy", arial(font_size), padding=(10,0))]
], bg="white", xalign=0)
year_leg = Image.from_column([Image.from_text("Monarchy ended", arial(font_size, bold=True)), year_arr], bg="white", xalign=0, padding=(0,5))

note_leg = Image.from_text("Map includes predecessor states like Bohemia, and non-resident monarchs like the Grand Duke of Finland, but not ancient Maceodonia or crusader Cyprus.", arial(font_size), max_width=200, bg="white", padding=(0,2))
legend = Image.from_column([year_leg, note_leg], bg="white", xalign=0, padding=5).pad(1, "black")
chart = map.place(legend, align=(1,0), padding=10)

# generate image grid
df = pd.read_csv("datasets/eumonarchies_timeline.csv")
tdata = pd.DataFrame([[df.loc[i+j] for j in range(12) if i + j < len(df)] for i in range(0,24,12)])
DEFAULT_IMG = "https://s-media-cache-ak0.pinimg.com/736x/0d/36/e7/0d36e7a476b06333d9fe9960572b66b9.jpg"

def process(img, d):
    return Image.from_column([
      img.crop_to_aspect(100, 100, (0.5, 0.2)).resize_fixed_aspect(width=100),
      Image.from_text(d['name'], arial(11, bold=True), max_width=100, fg="black", bg="white", align="center", padding=1),
      Image.from_text(d['description'], arial(11), max_width=100, fg="black", bg="white", align="center", padding=1)],
      bg="white")
    
grid = grid_chart(tdata, lambda d: None if none_or_nan(d) else get_non(d, "image_url", DEFAULT_IMG), process, yalign=0, bg="white", padding=1)

# title
title = Image.from_column([
Image.from_text("THE KING IS DEAD!", arial(48, bold=True)),
Image.from_text("end of European monarchies", arial(36))],
bg="white")

img = Image.from_column([title, chart, grid], bg="white", padding=2)
#img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)

img.save("output/eumonarchies.png")
