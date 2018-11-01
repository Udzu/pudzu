from pudzu.charts import *

FONT = calibri
BARBG = "#AAAAAA80"
SCALE = 2.65
s = lambda i: round(i * SCALE)
atlas = pd.read_csv("datasets/countries.csv").split_columns('country', "|").split_rows('country').set_index("country")
df = pd.read_csv("datasets/g20_deathpenalty.csv").assign_rows(parity = lambda d, i: (i+1) % 2).set_index("country")
df["pm"] = df["executions"] * 100000000 / atlas.loc[df.index].population
df["bar"] = 500 - df["pm"]

def rlabel(r):
    img = Image.from_row([
        Image.from_text(df.index[r].replace("\\n","\n"), FONT(s(16)), "black", align="center"),
        Image.from_url_with_cache(atlas.flag[df.index[r]]).convert("RGBA").resize((s(60),s(40))).trim(s(1)).pad(s(1), "grey")
    ], padding=(s(2),0))
    return img.pad_to_aspect(s(150),s(40),bg=None if df.parity[df.index[r]] else BARBG, align=1)

def labeler(c,r,v,h,w):
    if v > 300: l = "{}+ ({}+ executions)".format(format_float(v, 2), df.executions[df.index[r]])
    elif v > 100: l = "c.{} (1000s of executions*)".format(format_float(v, 2))
    elif non(df.type[df.index[r]]): l = "{} ({} executions)".format(format_float(v, 2), df.executions[df.index[r]])
    else: l = "0 ({})".format({"m": "ongoing moratorium", "o": "abolished for ordinary crimes", "a": "abolished for all crimes" }[df.type[df.index[r]]])
    return Image.new("RGBA", (w,h), None).place(Image.from_text(l, FONT(s(16)), "black"), align=(0,0.5), padding=s(2))
    
def label_if(pred):
    return lambda c,r,v,w,h: None if (pred( df.pm[df.index[r]]) != (c == 0)) else labeler(c,r, df.pm[df.index[r]], w, h)

def colorfn(c,r,v):
    if c == 0: return VegaPalette10.BLUE
    if not df.parity[df.index[r]]: return BARBG
    return None
    
chart = bar_chart(df[["pm", "bar"]], s(40), s(800), bg=None, horizontal=True, spacing=s(2), label_font=FONT(s(16)), rlabels=rlabel,
    type=BarChartType.STACKED,  colors= colorfn, clabels=label_if(artial(op.ge,100)),
    grid_interval=100, grid_width=s(1), ymax=500, ylabel=Image.from_text("number of executions per 100 million population in 2016", FONT(s(18)), padding=s(5)))

title = Image.from_text("Execution rates in G20 members in 2016".upper(), FONT(s(40), bold=True))
footer = Image.from_markup(
 # "**Data from Amnesty International Global Report 2016.**\n"
 # "[[https:\//www.amnesty.org/en/latest/news/2017/04/death-penalty-2016-facts-and-figures/]]\n\n"
 "* //The number of executions in China is a state secret.//"
 , partial(FONT, s(16)), padding=s(5))

img = Image.from_column([title, chart, footer], padding=s(5), bg="white")

# background = Image.from_url_with_cache("http://trueblueline.net/wp-content/uploads/2015/05/o-POLICE-LIGHTS-facebook.jpg").crop_to_aspect(img.width, img.height).resize(img.size).brighten(0.75)
# img = background.place(img)
# img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg=None, padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/g20_deathpenalty.png")
