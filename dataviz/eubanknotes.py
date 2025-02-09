from pudzu.charts import *
from pudzu.sandbox.bamboo import *
import seaborn as sns

df = pd.read_csv("datasets/eubanknotes.csv").set_index("country")
df.value = df.value.apply(int)

FONT = sans

CUTOFFS = [1000000000, 10000000, 1000000, 100000, 10000, 1000, 0]
PALETTE = [VegaPalette10.RED] + """#f1eef6
#d0d1e6
#a6bddb
#74a9cf
#3690c0
#0570b0
#034e7b""".split("\n")[::-1]

def colorfn(c):
    if c in ["Sea", "Borders", "Morocco", "Tunisia", "Algeria"]: return "white"
    elif c not in df.index: return "#A0A0A0"
    return PALETTE[next(i for i, x in enumerate(CUTOFFS) if df.value[c] >= x)]

def maybe_int(x):
    return int(x) if x == int(x) else x

def labelfn(c,w,h):
    if c in df.index:
        if c in ["Albania", "Cyprus", "Kosovo", "Malta", "Montenegro", "Slovenia", "Macedonia"]:
            label = f"**{df.value[c]:,}**\n**{df.currency[c]}**"
        else:
            nl = '\n' if df.value[c] <= 1000000 and c not in ["Estonia", "Latvia", "Lithuania", "Bosnia", "Croatia", "Bulgaria"] else ' '
            label = f"**{df.value[c]:,}**\n**{df.currency[c]}**{nl}[{df.year[c]}]"
            if c == "Hungary": label = label[:14] + "\n" + label[14:]
        fg = "white" if df.value[c] >= 10000 else "black"
        bg = "white" if fg == "black" else "black"
        text = Image.from_markup_bounded(label, (w,h), 24, partial(partial, FONT), fg, align="center", padding=2, min_font_size=7)
        return text and text.add_shadow(bg, blur=2, resize=False)

map = map_chart("maps/Europe.png", colorfn, labelfn)

HEADER = "Highest denomination"
LABELS = [ f"{j:,} or more" if i == 0 else f"less than {i:,}" if j == 0 else f"{j:,} or more" for i,j in generate_ngrams([0] + CUTOFFS, 2) ]
legend = generate_legend(PALETTE[:len(CUTOFFS)],  LABELS, box_sizes=40, header=HEADER, font_family=partial(FONT, 24))
chart = map.place(legend, align=(1,0), padding=20)

NOTES = [
    "https://upload.wikimedia.org/wikipedia/commons/3/33/HUP_100MB_1946_obverse.jpg",
    "https://i.pinimg.com/originals/c1/93/0e/c1930efc5d360f0510865b21c30c53a3.jpg",
    "https://i.redd.it/u7i35e3lcp701.jpg",
    "https://pbs.twimg.com/media/Cy-daaHWEAAz3CR.jpg",
    "https://www.leftovercurrency.com/app/uploads/2016/11/20000000-turkish-old-lira-banknote-7th-emission-group-1970-obverse-1.jpg",
]
notes = Image.from_column([Image.from_url_with_cache(note).convert("RGBA").resize_fixed_aspect(width=468) for note in NOTES])
chart = Image.from_row([notes, chart], yalign=0.5)

title = Image.from_column([
Image.from_text("HIGHEST DENOMINATION BANKNOTES BY COUNTRY", FONT(48, bold=True)),
Image.from_text('highest face value banknotes to have been in circulation [with year first issued]', FONT(36))],
bg="white", padding=2)

footer = Image.from_markup(
'//* the Bank of England also issues a non-circulating £100,000,000 banknote (to back the value of Scottish and Northern Irish banknotes)//'
, partial(arial, 24), "black", "white", max_width=chart.width-20, padding=(0,5,20,15))


img = Image.from_column([title, chart, footer], bg="white", padding=2)
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/eubanknotes.png")
img.convert("RGB").save("output/eubanknotes.jpg", quality=90)
