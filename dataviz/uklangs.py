from pudzu.charts import *

# generate map
df = pd.read_csv("datasets/uklangs.csv", index_col=0)

FONT = arial
CUTOFFS = [int(x * 10000) for x in [50, 20, 10, 5, 2, 1, 0]]
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

NAMES = { "Serbo-Croatian": "Bosnian, Croatian, Serbian, and Montenegrin", "Irish": "Gaelic (Irish)", "Scottish": "Scots", "Persian": "Persian or Farsi", "Ulster": "Ulster Scots", "Slovene": "Slovenian" }

def colorfn(c):
    c = NAMES.get(c, c)
    if c in ['Sea', 'Language Borders']: return "white"
    elif c in ['Country Borders']: return "#AAAAAA"
    elif c in ["English", "Welsh"]: return VegaPalette10.RED
    elif c not in df.index: return print(c) or PALETTE[-1]
    return PALETTE[next(i for i,x in enumerate(CUTOFFS) if df.Observation[c] >= x)]
    
def labelfn(c, w, h):
    d = c
    if c == "Scottish":
        label = f"Scots: {df.Observation['Scots']}\nGaelic: {df.Observation['Gaelic (Scottish)']}"
    elif c == "Irish":
        label = f"Irish: {df.Observation['Gaelic (Irish)']}"
    elif c == "Ulster":
        label = f"Ulster\nScots: {df.Observation['Ulster Scots']}"
    else:
        c = NAMES.get(c, c)
        if c not in df.index: return None
        label = f"{d}\n" + format(df.Observation[c], ",")
    return Image.from_text_bounded(label, (w, h), 24, papply(FONT, bold=True), align="center", padding=(0,0,0,2))
    
map = map_chart("maps/Eurolang3.png", colorfn, labelfn)

HEADER = "# \"main language\" speakers"
FOOTER = "////**EU total: 1,078,700 (0.21%)\nEurope total: 1,359,100 (0.17%)\nWorld total: 14,511,100 (0.20%)**"
LABELS = [ f"over {j:,}" if i == 0 else f"less than {i:,}" if j == 0 else f"{j:,} to {i:,}" for i,j in generate_ngrams([0] + CUTOFFS, 2) ]
legend = generate_legend([VegaPalette10.RED] + PALETTE, ["English & Welsh: 52.6m"] + LABELS + ["not listed explicitly"], box_sizes=40, header=HEADER, font_family=partial(FONT, 24))
chart = map.place(legend, align=(1,0), padding=20)

title = Image.from_column([
Image.from_text("EUROPEAN LANGUAGES SPOKEN IN ENGLAND AND WALES", FONT(48, bold=True)),
Image.from_text('number of "main language" speakers of each language according to the 2021 census', FONT(36))],
bg="white")
footer = Image.from_markup('Source: [[https:\//www.ons.gov.uk/census]]. Not shown here: //Kurdish// (66,446), //BSL// (21,631), "//other West or Central Asian languages//" (9,872), "//other Northern European languages (non EU)//" (7,876), //Yiddish// (5,353), "//other European languages (EU)//" (5,826), //Romany English// (1,900), //Cornish// (563), "//other Eastern European languages (non EU)//" (357), //Irish Traveller Cant// (36) and //Manx// (8).', partial(arial, 24), "black", "white", max_width=chart.width-120, padding=(0,5,20,5)) 


img = Image.from_column([title, chart, footer], bg="white", padding=2)
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/uklangs.png")
