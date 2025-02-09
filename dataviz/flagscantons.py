from math import gcd

from pudzu.charts import *
from pudzu.pillar import font_family

from pudzu.sandbox.bamboo import *

df = pd.read_csv("datasets/flagscantons.csv").set_index("country")
def togo(s):
    if "ϕ" in s:
        ϕ = (1 + 5 ** 0.5) / 2
        return ϕ * int(s[:-1])
    else:
        return int(s)

df["h"] = df["hn"] / df["hd"].apply(togo)
df["v"] = df["vn"] / df["vd"]
df["p"] = df["h"] * df["v"]
df = df.sort_values(["p"], ascending=False)

flags = pd.read_csv("datasets/countries.csv").split_columns('country', "|").explode('country').set_index('country')['flag']
flags["Georgia"] = "https://www.crwflags.com/fotw/images/g/ge_1990.gif"
flags["Myanmar"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/Flag_of_Myanmar_%281974%E2%80%932010%29.svg/1920px-Flag_of_Myanmar_%281974%E2%80%932010%29.svg.png"
flags["Abkhazia"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7a/Flag_of_the_Republic_of_Abkhazia.svg/1920px-Flag_of_the_Republic_of_Abkhazia.svg.png"
flags["CSA"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/3/32/Flag_of_the_Confederate_States_%281861%E2%80%931863%29.svg/1920px-Flag_of_the_Confederate_States_%281861%E2%80%931863%29.svg.png"
flags["Abu Dhabi"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d8/Flag_of_Abu_Dhabi.svg/1920px-Flag_of_Abu_Dhabi.svg.png"
flags["Orange Free State"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Flag_of_the_Orange_Free_State.svg/1280px-Flag_of_the_Orange_Free_State.svg.png"

FONT = font_family("fonts/Arial-Unicode")
SCALE = 2.25
s = lambda i: round(i * SCALE)
FONTSIZE = s(16)
BIGFONT = s(18)
SMALLFONT = s(14)
SUBTITLEFONT = s(18)
TITLEFONT = s(38)

def rlabel(r, horizontal):
    name = df.index[r]
    if get_non(df.comment, r):
        name += f"\n({df.comment[r]})"
    label = Image.from_text(name.replace("\\n","\n"), FONT(FONTSIZE), "black", beard_line=True, align="right")
    flag = Image.from_url_with_cache(flags[df.index[r].rstrip("¹²*")]).convert("RGBA")
    flag = flag.resize((s(48 * 1.5), s(48))).trim(s(1)).pad(s(1), "grey")
    if horizontal:
        return Image.from_row([label, flag], padding=(s(2),0))
    else:
        return Image.from_column([label, flag], padding=(0,s(2)))

def clabel(r):
    if df.index[r] == "Togo":
        return "9 / 25ϕ"
    n = df["hn"][r] * df["vn"][r]
    d = int(df["hd"][r]) * df["vd"][r]
    g = gcd(n, d)
    return f'{n // g} / {d // g}'

chart = bar_chart(df[["p"]], s(48), s(1000), bg="white", horizontal=True, spacing=s(2), label_font=FONT(FONTSIZE), rlabels=partial(rlabel, horizontal=True),
    clabels= { BarChartLabelPosition.INSIDE : lambda c,r,v: clabel(r) },
    ymax=0.3001, grid_interval=0.01, grid_width=s(0.5), tick_interval=0.01, label_interval=0.05,
    ylabels=lambda v: f"{round(v*100)}%",
    ylabel=Image.from_text("% of total flag area taken up by the canton (the rectangular inset on the top-left)", FONT(BIGFONT), padding=s(5))
)


title = Image.from_column([
Image.from_text("NATIONAL FLAGS BY CANTON SIZE", FONT(s(48), bold=True)),
#Image.from_text('proportion of flag taken up by the canton (the rectangular inset on the top left)', FONT(s(18)))
],
bg="white", padding=s(2))

footer = Image.from_markup(
"¹ also Taiwan, New Zealnd, Fiji, Samoa, Cook Islands, Tuvalu and Niue   ² also Uruguay"
, partial(FONT, s(16)), "black", "white", max_width=chart.width-20, padding=(0,5,20,15))


img = Image.from_column([title, chart, footer], bg="white", padding=2)
img = img.place(Image.from_text("/u/Udzu", FONT(s(16)), fg="black", bg=0, padding=s(5)).pad((s(1),s(1),0,0), "black"), align=1, padding=s(10))
img.save("output/flagscantons.png")
