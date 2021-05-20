from pudzu.charts import *
from pudzu.sandbox.bamboo import *
import scipy.stats

df = pd.read_csv("datasets/flagsrwbpercent.csv").set_index("country")

class HeraldicPalette(metaclass=NamedPaletteMeta):
    ARGENT = "#ffffff"
    AZURE = "#0f47af"
    GULES = "#da121a"
    SABLE = "#00ff00"

def flag_image(c):
    return Image.from_url_with_cache(df.flag[c]).convert("RGBA").remove_transparency("#00ff00").to_palette(HeraldicPalette).convert("RGBA")

def histogram(c):
    img = flag_image(c)
    cols = { next(n for n,p in zip(HeraldicPalette.names, HeraldicPalette) if RGBA(c) == p) : v for v,c in img.getcolors() if RGBA(c) != HeraldicPalette.SABLE}
    cols = valfilter(lambda v: v > 10000, cols)
    return valmap(lambda v: v / sum(cols.values()), cols)

df['histogram'] = [histogram(c) for c in df.index]
df["W"] = df["histogram"].apply(lambda x: x.get("ARGENT", 0)) * 100
df["R"] = df["histogram"].apply(lambda x: x.get("GULES", 0)) * 100
df["B"] = df["histogram"].apply(lambda x: x.get("AZURE", 0)) * 100

import ternary
from ternary.helpers import project_point
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

def getImage(c):
    flag = Image.from_url_with_cache(df.flag[c]).convert("RGBA").resize_fixed_aspect(height=40).pad(1 if c != "Nepal" else (1,0,0,0), "black")
    path = "cache/flags/{}.png".format(c)
    flag.save(path)
    return OffsetImage(plt.imread(path), dpi_cor=False)

figure, tax = ternary.figure(scale=100)
#tax.set_title("Color composition of Red-White-Blue flags".upper(), fontsize=16, pad=20, weight="heavy")
#tax.right_corner_label("red", fontsize=10)
#tax.top_corner_label("white", fontsize=10)
#tax.left_corner_label("blue", fontsize=10)
tax.bottom_axis_label("% red", fontsize=10, offset=0.07)
tax.right_axis_label("% white", fontsize=10, offset=0.14)
tax.left_axis_label("% blue", fontsize=10, offset=0.14)
tax.boundary(linewidth=2.0)
tax.gridlines(multiple=10, color="grey")

#points = df[['R', 'W', 'B']].values
#tax.scatter(points, marker='s', color='red')

for c in df.index:
    x, y = project_point(df[['R', 'W', 'B']].loc[c])
    ab = AnnotationBbox(getImage(c), (x, y), frameon=False)
    tax.get_axes().add_artist(ab)

tax.ticks(axis='lbr', linewidth=1, multiple=20, offset=0.02, tick_formats="%d%%")
tax.get_axes().axis('off')
tax.clear_matplotlib_ticks()

tax.savefig("cache/flags/flagsrwbpercent.png")

chart = Image.open("cache/flags/flagsrwbpercent.png").trim((0,40))
img = Image.from_column([
Image.from_text("Color composition of Red-White-Blue flags".upper(), sans(48, bold=True), padding=(0,10)),
chart], bg="white")
img.place(Image.from_text("/u/Udzu", sans(16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/flagsrwbpercent.png")

