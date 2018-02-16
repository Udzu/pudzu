import sys
sys.path.append('..')
from charts import *

FONT = calibri
atlas = pd.read_csv("datasets/countries.csv").split_columns('country', "|").split_rows('country').set_index("country")
df = pd.read_csv("datasets/g20_deathpenalty.csv").set_index("country")
df["pm"] = df["executions"] * 100000000 / atlas.loc[df.index].population

def rlabel(r):
    return Image.from_row([
        Image.from_text(df.index[r].replace("\\n","\n"), FONT(16), "black", align="center"),
        Image.from_url_with_cache(atlas.flag[df.index[r]]).convert("RGBA").resize((60,40)).trim(1).pad(1, "grey")
    ], padding=(2,0))

def labeler(c,r,v):
    if v > 300: return "{}+ ({}+ executions)".format(format_float(v, 2), df.executions[df.index[r]])
    elif v > 100: return "~{} (1000s of executions*)".format(format_float(v, 2))
    elif non(df.type[df.index[r]]): return "{} ({} executions)".format(format_float(v, 2), df.executions[df.index[r]])
    else: return "0 ({})".format({"m": "ongoing moratorium", "o": "abolished for ordinary crimes", "a": "abolished for all crimes" }[df.type[df.index[r]]])
    
def label_if(pred): # TODO: automate this bit
    return lambda c,r,v: None if not pred(v) else labeler(c,r,v)

chart = bar_chart(df[["pm"]], 40, 600, bg=None, horizontal=True, spacing=2, label_font=FONT(16), rlabels=rlabel,
    clabels= { BarChartLabelPosition.INSIDE : label_if(artial(op.ge,100)), BarChartLabelPosition.OUTSIDE: label_if(artial(op.lt,100)) },
    grid_interval=100, ymax=500, ylabel=Image.from_text("number of executions per 100 million population in 2016", FONT(18), padding=5))


title = Image.from_text("Execution rates in G20 members in 2016".upper(), FONT(40, bold=True))
footer = Image.from_markup(
 "**Data from Amnesty International Global Report 2016.**\n"
 "[[https:\//www.amnesty.org/en/latest/news/2017/04/death-penalty-2016-facts-and-figures/]]\n"
 "\n* //The number of executions in China is a state secret.//"
 , partial(FONT, 16), padding=5)

img = Image.from_column([title, chart, footer], padding=5)

background = Image.from_url_with_cache("http://trueblueline.net/wp-content/uploads/2015/05/o-POLICE-LIGHTS-facebook.jpg").crop_to_aspect(img.width, img.height).resize(img.size).brighten(0.75)
img = background.place(img)
img.place(Image.from_text("/u/Udzu", font("arial", 16), fg="black", bg=None, padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/g20_deathpenalty.png")
