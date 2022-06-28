from pudzu.charts import *
from pudzu.sandbox.bamboo import *
import seaborn as sns

df = pd.read_csv(f"datasets/euoscar.csv").set_index('country')

winners = tmap(RGBA, sns.color_palette("Blues", 6))
nominated = RGBA(204,85,85).brighten(0.25) #= tmap(RGBA, sns.color_palette("Reds", 6))[1]
nominated = RGBA(255,200,200).darken(0.2)
never = RGBA(215,215,215)

def colorfn(c):
    if c not in df.index:
        return "white" if c in ['Sea', 'Borders'] else never
    n = int(float(df.n[c].strip("*")))
    if n == 0:
        return nominated
    elif n > 4:
        return winners[-1]
    else:
        return winners[n]

@ignoring_exceptions
def labelfn(c):
    return df.n[c].lstrip("0")


map = map_chart("maps/Europe2.png", colorfn, labelfn, label_font=arial(28, bold=True))

legend = generate_legend(
    list(winners[5:0:-1]) + [nominated], [
    "5+ winners", "4 winners", "3 winners", "2 winners", "1 winner", "1+ nominations",
],
    font_family=partial(arial, 24),
)

chart = map.place(legend, align=(1,0), padding=10)

# title
title = Image.from_column([
Image.from_text("best international film oscar".upper(), arial(64, bold=True)),
Image.from_text("winners of the Academy Award for non-English language films produced outside the US", arial(28, italics=True)),
],
bg="white")

footer = """* includes 3 Russian-produced Soviet winners and 1 Ukrainian-produced nominee; 1 Slovak and 1 Czech winner from
Czechoslovakia; 1 winner from West Germany; and Yugoslav nominations produced in both Serbia and Croatia."""

subtitle = Image.from_text(footer, arial(24, italics=True), align="center", max_width=chart.width - 100, padding=10)

img = Image.from_column([title, chart, subtitle], bg="white", padding=2)
img.place(Image.from_text("/u/Udzu", arial(16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)

img.save(f"output/euoscar.png")

