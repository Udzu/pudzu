from pudzu.charts import *
from functools import cache

@cache
def ies(h, t):
    if not 0 <= h <= t:
        return 0
    elif h == t == 0:
        return 1
    elif (a:=ies(h, t-1)) == (b:=ies(h-1,t-1)) == 1:
        return 2
    else:
        return (a + b) % 2


def ies2(h, t):
    if not 0 <= h <= t: return 0
    if t % 2 == 0 and h % 2 == 1: return 2
    else: return 1


WIDTH = 48
assert round(WIDTH/4) == WIDTH/4

def stripe(w, h, reverse=False):
    # ugh
    s = Stripe((w, h), GradientColormap("black", None, "black"), intervals=(1,6,1))
    p = Rectangle((w//4, h//4), None)
    s.paste(p, (0,0))
    s.paste(p, (w-w//4,h-h//4))
    if reverse:
        s = s.transpose(Image.FLIP_LEFT_RIGHT)
    return s

def cell(h, t, W=WIDTH, ies=ies):
    H = round(W / (4/3))
    DOT_SIZE = round(W / 2.5)
    cell = Rectangle((W, H), "white")
    n = ies(h, t)
    if n == 0:
        return cell
    elif n == 1:
        cell.overlay(stripe(W//2, H), (0, H//2), copy=False)
        cell.overlay(stripe(W//2, H, True), (W//2, H//2), copy=False)
        if h + t != 0:
            if ies(h, t-1) == 1:
                offsets = Padding(0)
                cell = cell.pin(stripe(W // 2, H), (W//2+W//4, 0), offsets=offsets).trim(offsets)
            if ies(h-1, t - 1) == 1:
                offsets = Padding(0)
                cell = cell.pin(stripe(W // 2, H, True), (W//4, 0), offsets=offsets).trim(offsets)
        cell.place(Ellipse(DOT_SIZE, VegaPalette10.BLUE), copy=False)
    else:
        offsets = Padding(0)
        cell = cell.pin(stripe(W // 2, H), (W // 2 + W // 4, 0), offsets=offsets).trim(offsets)
        offsets = Padding(0)
        cell = cell.pin(stripe(W // 2, H, True), (W // 4, 0), offsets=offsets).trim(offsets)
        cell.place(Ellipse(DOT_SIZE, VegaPalette10.RED), copy=False)
    return cell


def triangle(n, ies=ies):
    rows = [Image.from_row([cell(h, t, ies=ies) for h in range(t+1)]) for t in range(n+1)]
    return Image.from_column(rows)

chart1 = triangle(10, ies=ies2)
chart2 = triangle(48)


cell1 = cell(0,1, 150)
cell1.place(Image.from_text("H", arial(24, bold=True)), align=(0,1), padding=20, copy=False)
cell1.place(Image.from_text("T", arial(24, bold=True)), align=(1,1), padding=20, copy=False)
#cell1.place(Image.from_text("H", arial(24, bold=True)), align=(1,0), padding=20, copy=False)

cell2 = cell(1,2,150)
cell2.place(Image.from_text("H", arial(24, bold=True)), align=(1,0), padding=20, copy=False)
cell2.place(Image.from_text("T", arial(24, bold=True)), align=(0,0), padding=20, copy=False)

legend = generate_legend([cell1.pad(10, None), cell2.pad(10, None)],
                         ["Toss the coin. Follow the left branch on H, right on T.",
                          "Stop. Select the result of the last toss."], font_family=partial(arial, 32),
                         header="procedure".upper(),
                         max_width=600,
                         footer="""The colour of each node is determined by its number of inbound edges //E//, which is easily calculated from its number of heads tosses //h// and total tosses //n//:

E(h, n) = 
  0, if h < 0 or h > n
  1, if h = n = 0
  2, if E(h, n-1) = E(h-1, n-1) = 1
  E(h, n-1) + E(h-1, n-1) mod 2, otherwise
  
This defines a cellular automaton that plots the Sierpiński triangle.""")

description = Image.from_column([Image.from_markup(
    """**BACKGROUND**
    
A well-known procedure for simulating a fair result from a biased coin (attributed to Von Neumann) is to toss it twice: if the results differ then use the last result, otherwise start over. We can in fact do better than this //by not discarding all the previous toss results when we toss again//.""",
    partial(arial, 32), max_width=600),
    chart1,
    Image.from_markup(
        """
The image above shows Von Neumann's solution, with red nodes representing toss histories that produce a result (based on the last toss), and blue nodes ones that require more tosses. The image to the right, meanwhile, shows the //most efficient// solution: e.g. with HHTT corresponding to a T result rather than more tosses.
    """,
        partial(arial, 32), max_width=600),
], xalign=0)

description = description.pad(10, "white").pad(1, "black")

chart = chart2.pad((200,50,0,0), "white")
chartleg = chart.remove_transparency("white").place(legend, (1, 0), padding=10).place(description, (0, 0), padding=10)

title = Image.from_text("Simulating fair results from a biased coin, efficiently".upper(), arial(80, bold=True), padding=10)
img = Image.from_column([title, chartleg], bg="white", padding=10)
img.place(Image.from_text("/u/Udzu", font("arial", 24), fg="black", bg="white", padding=10).pad((0,2,2,0), "black"), align=(0,1), padding=20, copy=False)
img.resize_fixed_aspect(scale=0.5).save("output/cointoss.png")
