from pudzu.charts import *
from pudzu.sandbox.bamboo import *

FONT = sans
BARBG = "#BBBBBB80" #"#AAAAAA80"
SCALE = 1 # 2.65
s = lambda i: round(i * SCALE)
df = pd.read_csv("datasets/calaccuracy.csv")
df["delta"] = np.abs(df["year"] - 365.24218967)


def rlabell(r,df):
    img = Image.from_column([
        Image.from_text(df.index[r].replace("\\n","\n"), FONT(s(16), bold=True), "black", beard_line=True, align="center", padding=1),
        Image.from_text("({})".format(df.origin[r].replace("\\n","\n")), FONT(s(16), italics=True), "black", beard_line=True,  align="center", padding=1),
    ], padding=(s(2),0), xalign=1).pad((s(2),0), None)
    return img.pad_to_aspect(s(210),s(40),bg=None if df.parity[df.index[r]] else BARBG, align=1)

def rlabelr(r,df):
    img = Image.from_text("{}".format(df.type[r].replace("\\n","\n")), FONT(s(16)), "black", beard_line=True, align="center", padding=2)
    img = img.pad_to_aspect(img.width, 40, bg=None)
    return img.pad_to_aspect(s(110),s(40),bg=None if df.parity[df.index[r]] else BARBG, align=0.5)
    
def labeler(c,r,v,h,w,df):
    l = df.accuracy[r]
    label = Image.from_text(l, FONT(s(16)), "black")
    return Image.new("RGBA", (w,h), None).place(label, align=(0,0.5), padding=(s(4),0))
    
def label_if(pred,df):
    return lambda c,r,v,w,h: None if (pred( df.delta[df.index[r]]) != (c == 0)) else labeler(c,r, df.delta[df.index[r]], w, h, df)

def colorfn(c,r,v, df):
    if c == 0:
        if df.index[r].startswith("Julian"): return VegaPalette10.ORANGE
        elif df.index[r].startswith("Mayan"): return VegaPalette10.PURPLE
        elif df.index[r].startswith("Islamic"): return VegaPalette10.GREEN
        return VegaPalette10.BLUE
    if not df.parity[df.index[r]]: return BARBG
    return None
    
fixed = df[df.delta < 0.01]
fixed["bar"] = 12/60/24 - fixed["delta"]
fixed = fixed.reset_index().assign_rows(parity = lambda d, i: (i+1) % 2).set_index("name")

maya = df[(df.delta > 10/24/60) & (df.delta < 12/24)].sort_values("delta", ascending=False)
maya["bar"] = 12/24 - maya["delta"]
maya = maya.reset_index().assign_rows(parity = lambda d, i: (i+1) % 2).set_index("name")

muslim = df[(df.delta > 1/24)].sort_values("delta", ascending=False)
muslim["bar"] = 12 - muslim["delta"]
muslim = muslim.reset_index().assign_rows(parity = lambda d, i: (i+1) % 2).set_index("name")

chart1 = bar_chart(
    fixed[["delta", "bar"]], s(40), s(1000), bg="white", horizontal=True, spacing=s(2), label_font=FONT(s(16)),
    rlabels={BarChartLabelPosition.BELOW: partial(rlabell,df=fixed), BarChartLabelPosition.ABOVE: partial(rlabelr,df=fixed)},
    type=BarChartType.STACKED, colors=partial(colorfn,df=fixed), clabels=label_if(artial(op.ge,0.001), fixed), 
    ymax=12/60/24, grid_interval=1/60/24, ylabels=lambda v: f"{round(v*60*24)}m",
)

chart2 = bar_chart(
    maya[["delta", "bar"]], s(40), s(1000), bg="white", horizontal=True, spacing=s(2), label_font=FONT(s(16)),
    rlabels={BarChartLabelPosition.BELOW: partial(rlabell,df=maya), BarChartLabelPosition.ABOVE: partial(rlabelr,df=maya)},
    type=BarChartType.STACKED, colors=partial(colorfn,df=maya), clabels=label_if(artial(op.ge,1/24), maya), 
    ymax=12/24, grid_interval=1/24, ylabels=lambda v: f"{round(v*24)}h",
)

chart3 = bar_chart(
    muslim[["delta", "bar"]], s(40), s(1000), bg="white", horizontal=True, spacing=s(2), label_font=FONT(s(16)),
    rlabels={BarChartLabelPosition.BELOW: partial(rlabell,df=muslim), BarChartLabelPosition.ABOVE: partial(rlabelr,df=muslim)},
    type=BarChartType.STACKED, colors=partial(colorfn,df=muslim), clabels=label_if(artial(op.ge,1), muslim), 
    ymax=12, grid_interval=1, ylabels=lambda v: f"{round(v)}d",
    ylabel=Image.from_text("average calendar drift from mean tropical year", FONT(s(18)), padding=s(10))
)

chart = Image.from_column([chart3, chart2, chart1], bg="white", padding=20)

TITLE = "Average accuracy of calendars relative to mean tropical year"
FOOTER = "* the Mayan Calendar used a 365-day 'vague year' cycle as well as a 260-day ritual cycle (and various combinations thereof)."

chart.save("output/calaccuracy.png")
