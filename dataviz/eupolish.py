from pudzu.charts import *

# generate map
df = pd.read_csv("datasets/eupolish.csv").set_index("country")
atlas = pd.read_csv("datasets/countries.csv").split_columns('country', "|").split_rows('country').set_index('country')

df["percapita"] = df["total"] * 100.0 / atlas.loc[df.index].population

FONT = arial
CUTOFFS = [10, 5, 2, 1, 0.5, 0.2, 0]
PALETTE = [
"#ece7f2", 
"#d0d1e6", 
"#a6bddb", 
"#74a9cf", 
"#3690c0", 
"#0570b0", 
 VegaPalette10.RED
]

PALETTE = PALETTE[::-1][:len(CUTOFFS)] + ["#d0d0d0"]

def colorfn(c):
    if c in ['Sea', 'Borders']: return "white"
    elif c == "Poland": return VegaPalette10.RED
    elif c not in df.index: return print(c) or PALETTE[-1]
    return PALETTE[next(i for i,x in enumerate(CUTOFFS) if df.percapita[c] >= x)]
    
def labelfn(c, w, h):
    if c not in df.index: return None
    label = format(round_significant(df.total[c],2), ",")
    return Image.from_text_bounded(label, (w, h), 24, papply(FONT, bold=True), align="center", padding=(0,0,0,2))
    
map = map_chart("maps/Europe2.png", colorfn, labelfn)

HEADER = "Polish population"
FOOTER = "////**Europe total: 5.8 million (0.7%)\nWorldwide total: 21 million (0.28%)**"
LABELS = [ f"over {j}%" if i == 0 else f"less than {i}%" if j == 0 else f"{j}% to {i}%" for i,j in generate_ngrams([0] + CUTOFFS, 2) ]
legend = generate_legend(PALETTE, LABELS + ["<100 individuals"], box_sizes=40, header=HEADER, footer=FOOTER, font_family=partial(FONT, 24))
chart = map.place(legend, align=(1,0))

title = Image.from_column([
Image.from_text("EUROPEAN POLISH DIASPORA, 2007", FONT(48, bold=True)),
Image.from_text("estimates by Stowarzyszenie „Wspólnota Polska”", FONT(36))],
bg="white")

img = Image.from_column([title, chart], bg="white", padding=2)
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black",padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/eupolish.png")
