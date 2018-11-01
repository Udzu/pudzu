from pudzu.charts import *
from pudzu.bamboo import *

# generate map
df = pd.read_csv("datasets/euexonyms.csv").set_index("country")
palette = ['#3c7f6b', '#79aa73']

def colorfn(c):
    if c in ['Sea', 'Borders']: return "white"
    elif c in ['Hungary', 'Finland', 'Germany', 'Greece', 'Albania']: return palette[0]
    elif c not in df.index: return "grey"
    else: return palette[1]
    
def labelfn(c, w,h):
    if c not in df.index: return None
    if c in ["Greece"]: sz = 12
    else: sz = 14
    return Image.from_column([
        Image.from_text(df.language[c], arial(sz, italics=True)),
        Image.from_text(df.name[c], arial(sz, bold=True), max_width=w, align="center"),
        Image.from_text(df.meaning[c], arial(10), max_width=w, align="center")
    ])
    
map = map_chart("maps/Europe.png", colorfn, labelfn)
legend = generate_legend(palette, [
"countries with English (and non-English) exonyms*.",
"countries with only non-English exonyms*."
], header="Type of exonym", footer="*only counting exonyms not derived from a borrowing or translation of the country's native name.", box_sizes=40, max_width=250)
chart = map.place(legend, align=(1,0), padding=10)

title = Image.from_column([
Image.from_text("A selection of European country exonyms".upper(), arial(48, bold=True)),
Image.from_text("country names not derived from the country's own name for itself", arial(36))],
bg="white")

img = Image.from_column([title, chart], bg="white", padding=2)
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/euexonyms.png")
