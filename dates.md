# [dates.py](dates.py)

## Summary 
Date classes supporting flexible calendars, date deltas and ranges.
 
## Dependencies
*Required*: [toolz](http://toolz.readthedocs.io/en/latest/index.html), [utils](utils.md).

*Optional*: [convertdate](https://pypi.python.org/pypi/convertdate/) (for non-Western calendar support).

## Documentation

### Calendars

The `Calendar` class represents a Year-Month-Day style calendar. The following `Calendar` objects are predefined:

 - `gregorian`: proleptic Gregorian calendar [default]
 - `julian`: proleptic Julian calendar
 - `isodate`: astronomical Gregorian calendar
 - `isoweek`: ISO week calendar (where 'months' are actually weeks)
 - `islamic`: Islamic calendar
 - `hebrew`: Hebrew calendar
 - `republican`: French Republican calendar

All but the first three require convertdate to be installed. All support dates before AD 1.

### Dates

The `Date` class represents a specific day in time, viewed under a specific calendar. Gregorian is the default.

```python
>> Date()
Sunday, 16 July 2017 [Gregorian]
>> Date((2017,2,1)) # can also init from Date, datetime.date or ordinal
Wednesday, 1 February 2017 [Gregorian]
>> Date((2017,2,1), format="{y:04d}/{m:02d}/{d:02d}")
2017/02/01 [Gregorian]
>> Date((2017,1,32))
InvalidDate: Invalid Gregorian date: YMD(year=2017, month=1, day=32)
```
    
Other calendars can be specified:
    
```python
>> Date((1917,10,25), calendar=julian)
Wednesday, 25 October 1917 [Julian]
>> Date((1917,10,25), calendar=julian).to_calenar(gregorian)
Wednesday, 7 November 1917 [Gregorian]
>> Date((1917,11,7)) == Date((1917,10,25), calendar=julian)
True
>> Date(calendar=isoweek)
Sunday, 2017-W28-7 [ISO week]
>> Date(calendar=islamic)
Sunday, 21 Shawwal 1438 AH [Islamic]
>> Date(calendar=republican)
Octidi, 28 Messidor 225 (Vesce) [French Republican]
```
    
Date details can be accessed directly:

```python
>> Date((2017,2,1)).ymd
YMD(year=2017, month=2, day=1)
>> Date((2017,2,1)).weekday
3
>> Date((2017,2,1)).ordinal
736361
```
    
Dates support basic day arithmetic (but see DateDeltas for more complex transitions):

```python
>> Date((2017,2,1)) + 100
Friday, 12 May 2017 [Gregorian]
>> Date() - Date((2017,2,1))
165
>> Date((2017,2,1)) < Date()
True
>> Date(1) # same ordinals as datetime
Monday, 1 January 1 [Gregorian]
>> Date(0) # AD/BC era has no year zero
Sunday, 31 December 1 BC [Gregorian]
```    
    
### DateDeltas

The `DateDelta` class represents a calendar-aware transition between dates. Unlike `datetime.timedelta`, these do not have to be of constant size. There are two main implementations: `DateInterval` and `DateFilter`. Furthermore, deltas can be combined using addition, subtraction, negation and mulitplication by an integer.

`DateInterval` represents an interval of a given number of years, months and days:

```python
>> DateInterval(years=2, months=1)
DateInterval(years=1,months=2)
>> DateInterval.from_dates((1917,11,7), Date(), gregorian)
DateInterval(years=99,months=8,days=9)

>> Date((2017,3,31))
Friday, 31 March 2017 [Gregorian]
>> Date((2017,3,31)) + DateInterval(months=2)
Wednesday, 31 May 2017 [Gregorian]
>> Date((2017,3,31)) + DateInterval(months=1)*2
Thursday, 1 June 2017 [Gregorian] # since April has only 30 days
>> Date((2017,3,31)) - DateInterval(days=1,months=2,years=3)
Thursday, 30 January 2014 [Gregorian]

>> Date((5776,6,1), hebrew)
Wednesday, 1 Adar A 5776 [Hebrew] # a leap month
>> Date((5776,7,1), hebrew)
Friday, 1 Adar B 5776 [Hebrew] # the non-leap month, confusingly
>> Date((5776,6,1), hebrew) + DateInterval(years=1)
Monday, 1 Adar 5777 [Hebrew] # not a leap year
>> Date((5776,7,1), hebrew) + DateInterval(years=1)
Monday, 1 Adar 5777 [Hebrew]
>> Date((5776,6,1), hebrew) + DateInterval(years=1) - DateInterval(years=1)
Friday, 1 Adar B 5776 [Hebrew]
```

`DateFilter` represents dates with a given property.

```python
>> Date()
Sunday, 16 July 2017 [Gregorian]
>> Date() + DateFilter(lambda d: d.ymd.day == d.calendar.days_in_month(d.ymd.year, d.ymd.month))
Sunday, 30 July 2017 [Gregorian] # last day of the month
>> Date() + DateFilter(lambda d: d.weekday == 1 and d.ymd.day <= 7)
Monday, 7 August 2017 [Gregorian] # first Monday of the month
>> Date() - DateFilter(lambda d: d.weekday == 1 and d.ymd.day <= 7) * 2
Monday, 5 June 2017 [Gregorian]
```
    
### DateRanges

The `DateRange` class represents a date range that spans one or more days. Ranges can be specified directly via a start and end time combined with a calendar:

```python
>> d = DateRange(Date()-10, Date())
>> d
6-16 July 2017 [Gregorian]
>> d.start
Thursday, 6 July 2017 [Gregorian]
>> d.end
Sunday, 16 July 2017 [Gregorian]
>> len(d)
11
>> Date() in d
True
>> d + DateInterval(months=1)
6-16 August 2017 [Gregorian]
>> d + (-DateInterval(months=1), DateInterval(months=1))
6 June-16 August 2017 [Gregorian]
```
    
Approximate dates can be specified using the `ApproximateDate` class, with a base date and precision level between `DatePrecision.DAY` and `DatePrecision.MILLENNIUM`. This also accepts a circa parameter (as in c. 1917) to specify a wider range of plus-or-minus 2 precision units.

```python
>> ApproximateDate(Date(), DatePrecision.MONTH)
July 2017 (month) [Gregorian]
>> len(_)
30
>> ApproximateDate(1997, DatePrecision.YEAR, circa=True)
c. 1997 (year) [Gregorian]
>> ApproximateDate(1997, DatePrecision.DECADE)
1990s (decade) [Gregorian]
>> Date() > ApproximateDate(1997, DatePrecision.DECADE)
True
```    
