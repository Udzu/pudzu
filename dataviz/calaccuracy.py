from pudzu.charts import *
from pudzu.sandbox.bamboo import *

"""
Comparing the accuracy of different calendars [OC]

**BACKGROUND**

The **solar year** is the time that the Sun takes to return to the same position in the cycle of seasons. This differs from the time it takes Earth to complete one full orbit around the Sun as measured with respect to the fixed stars (the sidereal year) due to the [precession of the equinoxes](https://en.wikipedia.org/wiki/Axial_precession) and [nutation](https://en.wikipedia.org/wiki/Nutation). Because the speed of the Earth varies in its elliptical orbit, the precise length of the solar year depends on which point you start measuring it from. The **mean solar year** averages this out.

This chart compares the accuracy of various calendars with respect to the mean solar year, as measured in 2000. Because the Earth's rotation is gradually slowing down, the mean solar year (as measured in Terrestrial Time) is actually decreasing by around 0.5s a century. However, this won't affect the comparison for at least a few thousand years.

Some comments about individual calendars:

* **Mayan Calendar**: despite its reputation for accuracy, the Mayan calendar was in fact a *floating* calendar "in which no attention was given to keeping the calendar in sync with the solar-agricultural year". The Mayan 'vague year' was 365 days long, while Long Counts were measured using 360-day cycles. There were no leap days.
* **Hebrew Calendar**: the 19-year Metonic cycle adopted by the Hebrew calendar (19 years ≈ 235 months) was actually discovered by the Babylonians and Chinese around 500BC.
* **Revised Julian Calendar**: the calendar used by around a third of Eastern Orthodox churches (such as Greece and Romania). While this is more accurate than the Gregorian calendar with respects to the mean solar year, the Gregorian is (currently) more accurate for the vernal equinox year, which is relevant for Easter. Orthodox Easter is still measured using the old Julian Calendar.
* **Chinese Calendar**: other calendars that use astronomical observations to stay in sync with the seasons include the lunisolar Hindu calendar and the solar Persian calendar.

**METHOD**

Generated using Python and [pillar](https://github.com/Udzu/pudzu-packages). Drifts calculated from year lengths as described on Wikipedia.

"""

FONT = sans
BARBG = "#BBBBBB80" #"#AAAAAA80"
SCALE = 1 # 2 # 1 #2.65
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
fixed = fixed.reset_index().assign_rows(parity = lambda d, i: (i+0) % 2).set_index("name")

maya = df[(df.delta > 10/24/60) & (df.delta < 12/24)].sort_values("delta", ascending=False)
maya["bar"] = 12/24 - maya["delta"]
maya = maya.reset_index().assign_rows(parity = lambda d, i: (i+0) % 2).set_index("name")

muslim = df[(df.delta > 1/24)].sort_values("delta", ascending=False)
muslim["bar"] = 12 - muslim["delta"]
muslim = muslim.reset_index().assign_rows(parity = lambda d, i: (i+0) % 2).set_index("name")

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
    ylabel=Image.from_text("average calendar drift from the mean solar year (365 days, 5 hours, 48 minutes, 45 seconds)", FONT(s(18)), padding=s(10))
)

chart = Image.from_column([chart3, chart2, chart1], bg="white", padding=20)

TITLE = "Comparing the accuracy of different calendars"
FOOTER = "* the Mayan Calendar used a 365-day 'vague year' cycle (//Haabʼ//), as well as a 260-day ritual cycle (//Tzolkʼin//) and a 360-day (//tun//)-based Long Count cycle."

title = Image.from_text_justified(TITLE.upper(), chart.width-50, 80, partial(sans, bold=True), bg="white", padding=(0,5))
footer = Image.from_markup(FOOTER, partial(sans, s(14)), max_width=chart.width-100, align="left", beard_line=True, bg="white", padding=(0,20,0,10))
img = Image.from_column([title, chart, footer], bg="white")
img = img.place(Image.from_text("/u/Udzu", FONT(s(16)), fg="black", bg=0, padding=s(5)).pad((s(1),s(1),0,0), "black"), align=1, padding=s(10))

img.save("output/calaccuracy.png")
