from pudzu.charts import *

FONT = calibri
BARBG = "#AAAAAA80"
atlas = pd.read_csv("datasets/countries.csv").split_columns('country', "|").explode('country').set_index("country")
df = pd.read_csv("datasets/g20_drinkingage.csv")
df = df.assign_rows(parity = lambda d, i: (i+1) % 2)
df = df.set_index("country")
df = df.assign_rows(gap = lambda d: get_non(d, 'max', d['min']) - d['min'])
df = df.assign_rows(illegal = lambda d, i: 0 if i not in ["Saudi Arabia", "India"] else 30 - d['max'])
df = df.assign_rows(bar = lambda d: 0 if d['parity'] else 30 - d['illegal'] - get_non(d, 'max', d['min']))

def rlabel(r):
    img = Image.from_row([
        Image.from_text(df.index[r].replace("\\n","\n"), FONT(16), "black", align="center"),
        Image.from_url_with_cache(atlas.flag[df.index[r]]).convert("RGBA").resize((60,40)).trim(1).pad(1, "grey")
    ], padding=(2,0))
    return img.pad_to_aspect(150,40,bg=None if df.parity[df.index[r]] else BARBG, align=1)

def label(c,r,v):
    if r == 0 and c == 2: return "illegal at any age"
    elif r == 0 or c > 0: return None
    elif r == 1: return "18-25 and illegal in some states"
    elif non(df['max'][df.index[r]]): return str(int(v))
    else: return "{}-{}".format(int(df['min'][df.index[r]]), int(df['max'][df.index[r]]))

chart = bar_chart(df[['min', 'gap', 'illegal', 'bar']], 40, 600, type=BarChartType.STACKED, bg=None, horizontal=True, spacing=2, label_font=FONT(16), rlabels=rlabel,
    clabels=label, colors= [VegaPalette10.BLUE, RGBA(VegaPalette10.BLUE).brighten(0.2), VegaPalette10.RED, BARBG],
    grid_interval=18, ymax=30, ylabel=Image.from_text("minimum age to buy a beer in public (or range if it depends on the state)", FONT(18, italics=True), padding=5))

title = Image.from_text("G20: Minimum age to buy a beer".upper(), FONT(40, bold=True))
img = Image.from_column([title, chart], padding=5)
background = Image.from_url_with_cache("http://trueblueline.net/wp-content/uploads/2015/05/o-POLICE-LIGHTS-facebook.jpg").crop_to_aspect(img.width, img.height).resize(img.size).brighten(0.75)
img = background.place(img)
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg=None, padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/g20_drinkingage.png")
