from pudzu.charts import *

# generate map
df = pd.read_csv("datasets/eujewish.csv").set_index("country")

FONT = arial
CUTOFFS = [10, 5, 2, 1, 0.5, 0.2, 0]
PALETTE = [
"#ece7f2", 
"#d0d1e6", 
"#a6bddb", 
"#74a9cf", 
"#3690c0", 
"#0570b0", 
"#034e7b"
]

#PALETTE = ["#d0d1e6", "#a6bddb", "#74a9cf", "#3690c0", "#0570b0", "#045a8d", "#023858"]
PALETTE = PALETTE[::-1][:len(CUTOFFS)] + ["#d0d0d0"]

def colorfn(c):
    if c in ['Sea', 'Borders']: return "white"
    elif c not in df.index: return print(c) or PALETTE[-1]
    return PALETTE[next(i for i,x in enumerate(CUTOFFS) if df.percapita[c] >= x)]
    
def labelfn(c, w, h):
    if c not in df.index: return None
    label = format(df.total[c], ",")
    return Image.from_text_bounded(label, (w, h), 24, papply(FONT, bold=True), align="center", padding=(0,0,0,2))
    
map = map_chart("maps/Europe2.png", colorfn, labelfn)

HEADER = "Jewish population per capita"
FOOTER = "////**EU total: 1,078,700 (0.21%)\nEurope total: 1,359,100 (0.17%)\nWorld total: 14,511,100 (0.20%)**"
LABELS = [ f"over {j/10:.1g}%" if i == 0 else f"less than {i/10:.1g}%" if j == 0 else f"{j/10:.1g}% to {i/10:.1g}%" for i,j in generate_ngrams([0] + CUTOFFS, 2) ]
legend = generate_legend(PALETTE, LABELS + ["unlisted (<100 individuals)"], box_sizes=40, header=HEADER, footer=FOOTER, font_family=partial(FONT, 24))
chart = map.place(legend, align=(1,0))

title = Image.from_column([
Image.from_text("EUROPEAN JEWISH POPULATIONS", FONT(48, bold=True)),
Image.from_text("core Jewish population estimates for 2017 (AJYB)", FONT(36))],
bg="white")

img = Image.from_column([title, chart], bg="white", padding=2)
#img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black",padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/eujewish.png")
