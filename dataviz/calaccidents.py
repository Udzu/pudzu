from pudzu.charts import *
from pudzu.sandbox.bamboo import *

def to_date(d):
    return Date(tmap(int, (d[6:], d[3:5], d[0:2])))
    
FONT = verdana
GRADIENT = GradientColormap("white", VegaPalette10.BLUE)
BANK_HOLIDAYS = tmap(to_date, [
    "03/01/2005", "25/03/2005", "28/03/2005", "02/05/2005", "30/05/2005", "29/08/2005", "26/12/2005", "27/12/2005",
    "02/01/2006", "14/04/2006", "17/04/2006", "01/05/2006", "29/05/2006", "28/08/2006", "25/12/2006", "26/12/2006",
    "01/01/2007", "06/04/2007", "09/04/2007", "07/05/2007", "28/05/2007", "27/08/2007", "25/12/2007", "26/12/2007",
    "01/01/2009", "10/04/2009", "13/04/2009", "04/05/2009", "25/05/2009", "31/08/2009", "25/12/2009", "28/12/2009",
    "01/01/2010", "02/04/2010", "05/04/2010", "03/05/2010", "31/05/2010", "30/08/2010", "27/12/2010", "28/12/2010",
    "03/01/2011", "22/04/2011", "25/04/2011", "29/04/2011", "02/05/2011", "30/05/2011", "29/08/2011", "26/12/2011", "27/12/2011",
    "02/01/2012", "06/04/2012", "09/04/2012", "07/05/2012", "04/06/2012", "05/06/2012", "27/08/2012", "25/12/2012", "26/12/2012",
    "01/01/2013", "29/03/2013", "01/04/2013", "06/05/2013", "27/05/2013", "26/08/2013", "25/12/2013", "26/12/2013",
    "01/01/2014", "18/04/2014", "21/04/2014", "05/05/2014", "26/05/2014", "25/08/2014", "25/12/2014", "26/12/2014"])

df = read_csvs("datasets/accidents/*csv")
df['Date'] = df['Date'].apply(to_date)
df["Count"] = 1
data = df[["Date", "Count", "Number_of_Casualties"]].groupby("Date").sum()

# bar charts

data["weekday"] = data.index
data["weekday"] = data["weekday"].apply(lambda d: d.weekday or 7)
data["holiday"] = data.index
data["holiday"] = data["holiday"].apply(lambda d: d in BANK_HOLIDAYS)
data["month"] = data.index
data["month"] = data["month"].apply(lambda d: d.ymd.month)
data["year"] = data.index
data["year"] = data["year"].apply(lambda d: d.ymd.year)

weekday_data = data.groupby("weekday").sum() / data.groupby("weekday").count() 
holiday_data = data.groupby("holiday").sum() / data.groupby("holiday").count()
weekday_data.loc[8] = holiday_data.loc[True]
month_data = data.groupby("month").sum() / data.groupby("month").count()
year_data = data.groupby("year").sum() / data.groupby("year").count()

df["time"] = df["Time"].apply(ignoring_exceptions(lambda t: int(t[:2])))
hour_data = df[["Count", "time"]].groupby("time").count() / 1000

weekdays = bar_chart(weekday_data[['Count']], 90, 225, spacing=6, ymax=550, colors=lambda c,r: VegaPalette10.LIGHTGREEN if r == 7 else VegaPalette10.GREEN if r >= 5 else VegaPalette10.RED if r == 4 else VegaPalette10.BLUE,
                    rlabels=lambda i: "Bank Holiday" if i == 7 else WesternCalendar.WEEKDAYS[(i+1) % 7], clabels = { BarChartLabelPosition.INSIDE : lambda c,r,v: format_float(v, 3) },
                    grid_interval=100, label_interval=100, label_font=FONT(14, bold=False),
                    ylabel=Image.from_text("average # incidents per day", FONT(14), padding=(5,2,5,10)).transpose(Image.ROTATE_90),
                    xlabel=Image.from_text("day of week", FONT(14), padding=5))

months = bar_chart(month_data[['Count']], 60, 225, spacing=4, ymax=550, colors=lambda c,r: VegaPalette10.GREEN if r in [0, 1, 2, 3] else VegaPalette10.RED if r == 10 else VegaPalette10.BLUE,
                    rlabels=lambda i: WesternCalendar.MONTHS[i].upper()[:3], clabels = { BarChartLabelPosition.INSIDE : lambda c,r,v: format_float(v, 3) },
                    grid_interval=100, label_interval=100, label_font=FONT(14, bold=False),
                    ylabel=Image.from_text("average # incidents per day", FONT(14), padding=(5,2,5,10)).transpose(Image.ROTATE_90),
                    xlabel=Image.from_text("month of year", FONT(14), padding=5))

hours = bar_chart(hour_data[['Count']], 30, 225, spacing=2, ymax=150, colors=lambda c,r: VegaPalette10.RED if r in [8,17] else VegaPalette10.GREEN if r in [4] else VegaPalette10.BLUE,
                    rlabels=lambda i: str(i), clabels = { BarChartLabelPosition.INSIDE : lambda c,r,v: str(int(round(v))) }, ylabels = "{}k",
                    grid_interval=25, label_interval=25, label_font=FONT(14, bold=False),
                    ylabel=Image.from_text("total # incidents (in thousands)", FONT(14), padding=(5,2,5,10)).transpose(Image.ROTATE_90),
                    xlabel=Image.from_text("hour of day", FONT(14), padding=5))

years = bar_chart(year_data[['Count']], 80, 225, spacing=5, ymax=550, colors=lambda c,r: VegaPalette10.RED if r in [0] else VegaPalette10.GREEN if r in [7] else VegaPalette10.BLUE,
                    rlabels=lambda i: str(year_data.index[i]), clabels = { BarChartLabelPosition.INSIDE : lambda c,r,v: format_float(v, 3) },
                    grid_interval=100, label_interval=100, label_font=FONT(14, bold=False),
                    ylabel=Image.from_text("average # incidents per day", FONT(14), padding=(5,2,5,10)).transpose(Image.ROTATE_90),
                    xlabel=Image.from_text("year", FONT(14), padding=5))

bars = Image.from_column([hours, weekdays, months, years], bg="white", padding=5)

# calendar chart

def bgfn(d, w, h, *, data=None):
    bg = Rectangle((w,h), RGBA(GRADIENT(data.Count[d] / data.max().Count, bytes=True)))
    if d in BANK_HOLIDAYS: bg = bg.place(Triangle((w//4, h//3), VegaPalette10.RED, p=0).transpose(Image.FLIP_TOP_BOTTOM), align=0)
    return bg

def year(y):
    year_data = data.loc[(data.index >= Date((y,1,1))) & (data.index < Date((y+1,1,1)))]
    month_imgs = [month_chart(Date((y,m,1)), day_start=1, day_bg=partial(bgfn, data=year_data), month_label="{M}", month_bg="#E0E0E0", fonts=partial(FONT, 16)) for m in range(1,13)]
    months = Image.from_array(list(generate_batches(month_imgs, 3)), padding=10, bg="white", yalign=0)
    return months

calendar = year(2014)

# combine

cal_title = Image.from_multitext(["daily road accidents during 2014", " (bank holidays marked red)"], [FONT(40, bold=True), FONT(28, bold=True)])
bar_title = Image.from_text("road accidents during 2005–2014", FONT(40, bold=True))
chart = Image.from_row([Image.from_column([cal_title, calendar], padding=5), Image.from_column([bar_title, bars], padding=5)])

img_title = Image.from_text("The safest times to drive in the UK".upper(), FONT(60, bold=True))
img_footer = Image.from_markup("Accident data from the UK Department of Transport, collated by [[https:\//www.kaggle.com/daveianhickey/2000-16-traffic-flow-england-scotland-wales]].", partial(FONT, 24))
img = Image.from_column([img_title, chart, img_footer], bg="white", padding=10)

img.place(Image.from_text("/u/Udzu", font("arial", 14), fg="black", bg="white", padding=5).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/calaccidents.png")