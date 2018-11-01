from pudzu.charts import *
from pudzu.bamboo import *
import seaborn as sns

# generate map
df = pd.read_csv("datasets/euheight.csv").set_index("country").fillna(0)
palette = tmap(RGBA, sns.cubehelix_palette(7, start=0.5, rot=-0.85))
basketball = Image.open("icons/basketball.png").convert("RGBA").resize((18,18))

def colorfn(c):
    if c not in df.index:
        return "white" if c in ['Sea', 'Borders'] else "grey"
    return palette[(int(df['height'][c]) - 172) // 2]
    
def labelfn(c):
    if c not in df.index or df['eurobasket'][c] == 0:
        return None
    return Image.from_row([basketball]*int(df['eurobasket'][c]), bg=0, padding=2)
    
map = map_chart("maps/Europe.png", colorfn, labelfn)

# legend
legendboxes = Image.from_array([
[Image.new("RGBA", (40,40), palette[i]),
 Image.from_text("{}-{} cm".format(i * 2 + 172, str(i * 2 + 174)[-1]), arial(16))]
 for i in reversed(range(6))] + [
[Image.new("RGBA", (40,40), "grey"), Image.from_text("No data", arial(16))],
[Image.new("RGBA", (40,40), "white").place(basketball), Image.from_text("Eurobasket wins\nsince 1993*", arial(16))]
], xalign=(0.5, 0), padding=(3,0), bg="white")
legend = Image.from_column([
Image.from_text("Heights", arial(16, bold=True), padding=5),
legendboxes,
Image.from_text("* Eurobasket wins for\nFRY are under Serbia.", arial(16, italics=True), align="left")
], bg="white", xalign=0).pad(5, "white").pad(1, "black")
chart = map.place(legend, align=(1,0), padding=10)

# title
title = Image.from_column([
Image.from_text("AVERAGE 18 YEAR OLD MALE HEIGHT (2014)", arial(48, bold=True)),
Image.from_text("and number of Eurobasket wins since 1993", arial(36))],
bg="white")

# title = Image.from_text("Europe by number of, and longest borders", arial(48, bold=True), bg="white")
img = Image.from_column([title, chart], bg="white", padding=2)
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/euheight.png")
