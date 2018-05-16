import sys
sys.path.append('..')
from charts import *

def to_date(d):
    return Date(tmap(int, (d[6:], d[3:5], d[0:2])))

# TODO: add other years, holiday dates
# TODO: prettify calendar

df = pd.read_csv("datasets/accidents/accidents_2012_to_2014.csv")
df['Date'] = df['Date'].apply(to_date)
df["Count"] = 1
data = df[["Date", "Count", "Number_of_Casualties"]].groupby("Date").sum()

FONT = verdana
GRADIENT = GradientColormap("white", VegaPalette10.RED)

BANK_HOLIDAYS = [
    "02/01/2012", "06/04/2012", "09/04/2012", "07/05/2012", "04/06/2012", "05/06/2012", "27/08/2012", "25/12/2012", "26/12/2012",
    "01/01/2013", "29/03/2013", "01/04/2013", "06/05/2013", "27/05/2013", "26/08/2013", "25/12/2013", "26/12/2013",
    "01/01/2014", "18/04/2014", "21/04/2014", "05/05/2014", "26/05/2014", "25/08/2014", "25/12/2014", "26/12/2014"]
    
BANK_HOLIDAYS = tmap(to_date, BANK_HOLIDAYS)
SCHOOL_HOLIDAYS = [DateRange((2013,12,21), (2014,1,5)), # TODO: 2012, 2013
                   DateRange((2014,2,15),(2014,2,23)), DateRange((2014,4,5),(2014,4,21)), DateRange((2014,5,24), (2014,6,1)),
                   DateRange((2014,7,23),(2014,8,31)), DateRange((2014,10,25),(2014,11,2)), DateRange((2014,12,20),(2015,1,4))]

def bgfn(d, w, h, *, data=None):
    bg = Rectangle((w,h), RGBA(GRADIENT(data.Count[d] / data.max().Count, bytes=True)))
    if d in BANK_HOLIDAYS: bg = bg.place(Rectangle((w, h//4), VegaPalette10.PURPLE), align=0)
    elif any(d in hol for hol in SCHOOL_HOLIDAYS): bg = bg.place(Rectangle((w, h//4), VegaPalette10.BLUE), align=0)
    return bg

def year(y):
    year_data = data.loc[(data.index >= Date((y,1,1))) & (data.index < Date((y+1,1,1)))]
    month_imgs = [month_chart(Date((y,m,1)), day_start=1, day_bg=partial(bgfn, data=year_data), month_label="{M}", month_bg="#E0E0E0", fonts=partial(FONT, 16)) for m in range(1,13)]
    months = Image.from_array(list(generate_batches(month_imgs, 4)), padding=10, bg="white", yalign=0)
    return months
    
# calendar = year(2014)

data["weekday"] = data.index
data["weekday"] = data["weekday"].apply(lambda d: d.weekday or 7)
data["holiday"] = data.index
data["holiday"] = data["holiday"].apply(lambda d: "2Bank Holidays" if d in BANK_HOLIDAYS else "1School Holidays" if any(d in h for h in SCHOOL_HOLIDAYS) else "0School Term-time")

weekday_data = data.groupby("weekday").sum() / data.groupby("weekday").count() 
holiday_data = data.groupby("holiday").sum() / data.groupby("holiday").count()

weekday = bar_chart(weekday_data[['Count']], 90, 600, spacing=5, ymax=500, colors=lambda c,r: VegaPalette10.RED if r >= 5 else VegaPalette10.BLUE,
                    rlabels=lambda i: gregorian.WEEKDAYS[(i+1) % 7], grid_interval=100, label_interval=100, label_font=FONT(14, bold=False))

holiday = bar_chart(holiday_data[['Count']], 90, 600, spacing=5, ymax=500, colors=lambda c,r: VegaPalette10[r],
                    rlabels=lambda i: holiday_data.index[i][1:].replace(" ","\n"), grid_interval=100, label_interval=100, label_font=FONT(14, bold=False))

