from pudzu.charts import *
from pudzu.dates import *
from itertools import accumulate

# HORRIBLE HACK FOR NOW SINCE MONTH_CHARTS CAN'T COPE WITH LEAP WEEKDAYS

WEEKEND_BG = "#9ecae1"

class MyCalendar(Calendar):

    MONTHS = ("January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December")
    WEEKDAYS = ("Monday", "Wednesday", "Thursday", "Friday", "Sunday")
    DAYS_IN_MONTH = (30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 35)
    
    def __init__(self):
        self.DIMS = [0]+ list(accumulate(self.DAYS_IN_MONTH))
    
    @property
    def calendar_name(self):
        return "mine"

    def year_name(self, ymd):
        return str(ymd.year)
        
    def days_in_month(self, year, month): 
        return self.DAYS_IN_MONTH[month-1]
        
    def months_in_year(self, year):
        return 12
        
    def date_to_ordinal(self, ymd):
        y = ymd.year
        d = self.DIMS[ymd.month-1] + ymd.day
        return (Date((ymd.year, 1, 1))+(d-1)).ordinal
        
    def ordinal_to_date(self, ordinal):
        ymd = gregorian.ordinal_to_date(ordinal)
        days = ordinal - gregorian.date_to_ordinal(YMD(ymd.year,1,1))
        month, day = next((i,days-self.DIMS[i-1]) for i,dim in enumerate(self.DIMS) if days < dim)
        return YMD(ymd.year, month, day+1)

cal = MyCalendar()

class MyCalendarLeap(MyCalendar):

    WEEKDAYS = ("Monday","Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
    DAYS_IN_MONTH = (30, 36, 30)
    
    def __init__(self):
        self.DIMS = [0]+ list(accumulate(self.DAYS_IN_MONTH))
    
    def weekday(self, ymd, ordinal):
        return (ordinal - 1) % len(self.WEEKDAYS)
    
    def days_in_month(self, year, month): 
        return 36

cal2 = MyCalendarLeap()

def bgfn(d, w, h):
    if d.ymd.month != 2:
        weekend = (d.ymd.day % 5 == 0) or (d.ymd.day % 10 == 4)
    elif (d.ymd.day % 6 == 5) and d.ymd.day != 35:
        return "grey" # fake day
    else:
        weekend = (d.ymd.day % 6 == 0) or (d.ymd.day % 12 == 4) or d.ymd.day == 35
    bg = WEEKEND_BG if weekend else "white"
    if d.ymd.month == 2 and d.ymd.day == 35: bg = Stripe(10, bg, "white")
    rec = Rectangle((w,h), bg)
    g = d - d.ymd.day // 6 if d.ymd.month == 2 else d
    if d.ymd.day == 36: g += 1
    greg = g.to_calendar(calendar=gregorian)
    rec = rec.place(Image.from_text("{} {}".format(greg.date_format("{d}"), greg.date_format("{M}")[:3].upper()), arial(10), VegaPalette10.RED if greg.ymd.day == 1 else "#A0A0A0", beard_line=True), align=(0,1))
    return rec

def fgfn(d, w, h):
    if d.ymd.month == 2:
        if d.ymd.day == 35: return "29½"
        elif (d.ymd.day % 6 == 5): return None
        else: d -= d.ymd.day // 6
    return d.date_format("{D}")
    
def month(m):
    return month_chart(Date((2018 if m != 2 else 2020,m,1), calendar=cal if m != 2 else cal2), day_label=fgfn, month_label="{M}", day_bg=bgfn, month_bg="#E0E0E0", fonts=partial(arial, 16))
    
month_imgs = [month(m) for m in range(1,13)]
months = Image.from_array(list(generate_batches(month_imgs, 3)), padding=10, bg="white", yalign=0)

# title etc

TITLE = "12-month metric calendar proposal"

LEGEND = """**SUMMARY**

• 5 day weeks, with alternating
   one and two day weekends
   
• 30 day months, apart from
   December which has 35 days
   
• leap years have an additional
   day between 29 and 30 February

  
**ADVANTAGES**

• **weeks are aligned with months and years**
   both start on Monday and end on Sunday
   
• **weekdays are obvious from the date**
   no need even for your 7 times table!
   
• **there's a year-independent conversion
   to and from the Gregorian calendar**
   
• **there are slightly more weekends**
   110 versus 104/5 on non-leap years
   
• **familiar month and weekday names**

• **no more Tuesdays**

• **no more Friday 13th**


**DISADVANTAGES**

• **birthdays are always on the same weekday**

• **December is 15% longer**
   compared to February being 10% shorter
  
• **less business for calendar makers**
"""

box = generate_legend([WEEKEND_BG,
Rectangle(40, Stripe(10, WEEKEND_BG, "white")),
Rectangle(40, "white").place(Image.from_text("2 FEB", arial(10), "#A0A0A0", beard_line=True))
], ["weekend", "leap day (leap years only)", "equivalent Gregorian date"], font_family=partial(arial, 16))
title = Image.from_text(TITLE.upper(), arial(60, bold=True), bg="white")
legend = Image.from_markup(LEGEND, partial(arial, 24), bg="white")
img = Image.from_column([title, Image.from_row([months, Image.from_column([box, legend], padding=(0,10), xalign=0)], padding=5)], padding=20, bg="white")
img.save("output/calming.png")


