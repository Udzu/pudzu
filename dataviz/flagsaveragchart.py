import sys
sys.path.append('..')
from charts import *
from statistics import mean
from colorsys import rgb_to_hls, hls_to_rgb

flags = pd.read_csv("datasets/countries.csv").filter_rows("organisations >> un").update_columns(country=lambda s: s.split("|")[0]).set_index("country").flag
SIZE = (60, 40)

def to_linear(srgb):
    c = srgb / 255
    return np.where(c <= 0.04045, c / 12.92, ((c+0.055)/1.055)**2.4)

def from_linear(lrgb):
    c = np.where(lrgb <= 0.0031308, 12.92 * lrgb, (1.055)*lrgb**(1/2.4)-0.055)
    return np.round(c * 255)

def colorfn(c):
    if c not in flags.index: return "white" if c in ['Sea', 'Borders'] else "grey"
    flag_array = np.array(Image.from_url_with_cache(flags[c]).to_rgba().remove_transparency("white").convert("RGB"))
    float_average = [ from_linear(to_linear(flag_array[:,:,i]).mean()) for i in range(flag_array.shape[-1])]
    return RGBA([int(f) for f in float_average])
    
colormap = { k : colorfn(k) for k in flags.index }
hlsmap = { k : rgb_to_hls(*[c/255 for c in rgba[:3]]) for k, rgba in colormap.items() }

# HUE
by_hue =  { (i+0.5) / 36 : [ (k,c) for k,c in hlsmap.items() if i / 36 <= c[0] < (i+1) / 36 ] for i in range(36) }
counts_hue = pd.DataFrame([len(v) for v in by_hue.values()], index=by_hue.keys(), columns=["number"])
counts_hue = counts_hue.reindex(index=np.concatenate([counts_hue.index[18:], counts_hue.index[:18]]))

def rlabel(r):
    return Rectangle(SIZE, RGBA(hls_to_rgb(counts_hue.index[r], 0.5, 0.7)))
    
def clabel(c,r,v):
    countries = [c for c,_ in sorted(by_hue[counts_hue.index[r]], key=lambda p: -p[1][1])]
    flagimgs = [Image.from_url_with_cache(flags[c]).to_rgba().remove_transparency("white").resize(SIZE).trim(1).pad(1, "grey") for c in countries]
    return Image.from_column(flagimgs) if flagimgs else None

chart = bar_chart(counts_hue, SIZE[0], SIZE[1]*32, spacing=5,
                  ymax=32, grid_interval=5, label_font=verdana(24),
                  rlabels=rlabel, clabels={ BarChartLabelPosition.INSIDE : clabel })

title = Image.from_text("Flags of the world, sorted by average hue".upper(), verdana(80, bold=True), padding=(0,0,0,2))
subtitle = Image.from_text("calculated from flag images on Wikipedia, averaged using sRGB gamma-correction", verdana(60, italics=True), padding=(0,0,0,20))
img = Image.from_column([title, subtitle, chart], bg="white").pad(10, "white")
img.save("output/flagsaveragechart.png")
