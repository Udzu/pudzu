from pudzu.charts import *
from pudzu.sandbox.bamboo import *

FONT = sans
BARBG = "#AAAAAA80"
SCALE = 1 # 2.65
s = lambda i: round(i * SCALE)
df = pd.read_csv("datasets/calaccuracy.csv").assign_rows(parity = lambda d, i: (i+1) % 2).set_index("name")
df["delta"] = np.abs(df["year"] - 365.24218967)


df["bar"] = 12/60/24 - df["delta"]
df = df[df.bar > 0]


def rlabel(r):
    img = Image.from_column([
        Image.from_text(df.index[r].replace("\\n","\n"), FONT(s(16), bold=True), "black", beard_line=True, align="center"),
        Image.from_text("({})".format(df.origin[r].replace("\\n","\n")), FONT(s(16), italics=True), "black", beard_line=True,  align="center"),
    ], padding=(s(2),0), xalign=1).pad((s(2),0), None)
    return img.pad_to_aspect(s(210),s(40),bg=None if df.parity[df.index[r]] else BARBG, align=1)

def labeler(c,r,v,h,w):
    l = df.accuracy[r]
    return Image.new("RGBA", (w,h), None).place(Image.from_text(l, FONT(s(16)), "black"), align=(0,0.5), padding=(s(4),0))
    
def label_if(pred):
    return lambda c,r,v,w,h: None if (pred( df.delta[df.index[r]]) != (c == 0)) else labeler(c,r, df.delta[df.index[r]], w, h)

def colorfn(c,r,v):
    if c == 0: return VegaPalette10.BLUE
    if not df.parity[df.index[r]]: return BARBG
    return None
    
chart = bar_chart(df[["delta", "bar"]], s(40), s(800), bg="white", horizontal=True, spacing=s(2), label_font=FONT(s(16)), rlabels=rlabel, 
    type=BarChartType.STACKED, colors=colorfn, clabels=label_if(artial(op.ge,0.001)),
#    grid_interval=100, grid_width=s(1), ymax=500, ylabel=Image.from_text("number of executions per 100 million population in 2016", FONT(s(18)), padding=s(5))
)
chart.save("output/calaccuracy.png")
