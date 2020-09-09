from pudzu.charts import *
from pudzu.sandbox.bamboo import *

# generate map
df = pd.read_csv("datasets/eudecimal.csv").set_index("country")
PALETTE = ['#a1dab4', '#41b6c4', '#225ea8']
PALETTE = [VegaPalette10.GREEN, VegaPalette10.BLUE, VegaPalette10.RED]
FONT = sans

def colorfn(c):
    if c in ['Sea', 'Borders']: return "white"
    elif c not in df.index: return "grey"
    if df.year[c] < 1800: col = PALETTE[0]
    elif df.year[c] < 1900: col = PALETTE[1]
    else: col = PALETTE[2]
    if df.currency[c].startswith("("): col = RGBA(col).brighten(0.5)
    return col
    
def labelfn(c, w,h):
    if c not in df.index: return None
    if df.currency[c].startswith("("): return None
    label = f"{df.currency[c]}\n({df.year[c]})"
    return Image.from_text_bounded(label, (w, h), 24, papply(FONT, bold=True), align="center")
    
map = map_chart("maps/Europe.png", colorfn, labelfn)
 # Sardinia-Piedmont introduced lira in 1816
legend = generate_legend(PALETTE, [
"**18th century**",
"**19th century**",
"**20th century**",
], header="Decimal currency adoption".upper(),
footer="""A lighter shade indicate countries that decimalised while using another country's currency.

* Sardinia introduced the decimal lira in 1816.""", box_sizes=40, max_width=350, font_family=partial(FONT, 16))
chart = map.place(legend, align=(1,0), padding=10)

title = Image.from_column([
Image.from_text("Currency decimalisation in Europe".upper(), arial(48, bold=True)),
Image.from_text("dates of switch to currencies related by powers of 10", arial(36))],
bg="white")

img = Image.from_column([title, chart], bg="white", padding=2)
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/eudecimal.png")
