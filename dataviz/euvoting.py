import seaborn as sns
from pudzu.charts import *
from pudzu.experimental.bamboo import *

df = pd.read_csv("datasets/euvoting.csv").set_index('country')
palette = tmap(RGBA, sns.color_palette("Blues", 4))
palette = ['#0194a8', '#9cd1c8', '#afcb8f', '#fa9e7d']

# colors = sns.cubehelix_palette(6, start=1.5, rot=-1, dark=.25)
# palette = [RGBA(c) for c in colors]

def colorfn(c):
    if c not in df.index:
        return "white" if c in ['Sea', 'Borders'] else "grey"
    if c == "Vatican City":
        return RGBA(204,85,85,255)
    abolished = df['full'][c]
    dates = [1914, 1939, 1960, 2000]
    i = next(i for i,d in enumerate(dates) if abolished < d)
    return palette[i]

def labelfn(c):
    if c not in df.index:
        return None
    abolished = str(df['full'][c])
    partial = "" if non(df['partial'][c]) else "({})\n".format(df['partial'][c])
    return Image.from_text(partial+abolished, arial(16, bold=True), align='center')
    
map = map_chart("maps/Europe.png", colorfn, labelfn)

legend = generate_legend(treversed(palette),
                         treversed(["Pre 1914", "Post 1914", "Post 1939", "Post 1960"]),
                         font_family=partial(arial, size=16),
                         header="Equal suffrage achieved", 
                         footer="The dates in parentheses are when at least some women got the right to vote in national elections.",
                         max_width=150)
chart = map.place(legend, align=(1,0), padding=10)
chart.save("output/euvoting.png")

title = Image.from_column([
Image.from_text("WOMEN'S SUFFRAGE IN EUROPE", arial(48, bold=True)),
Image.from_text("dates when women got equal voting rights to men", arial(36))],
bg="white")

footer = Image.from_text(
"¹ Swedish women who were taxpaying guild members could vote during the Age of Liberty (1718-1772).\n"
"² Portuguse women were also accidentally enfranchised in 1911 but the law was changed to prevent this in 1913.\n"
"³ Swiss women got full federal voting rights in 1971, but were only fully enfranchised at the Canton level in 1990.                                         "
, arial(18))

img = Image.from_column([title, chart, footer], bg="white", padding=2)
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/euvoting.png")
