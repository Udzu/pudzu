import abc as ABC
import collections.abc
import datetime

from enum import Enum
from functools import reduce, total_ordering
from numbers import Integral
from collections import namedtuple

from pudzu.utils import *

cdate = optional_import("convertdate")

# Date class supporting flexible calendars, deltas and ranges

# Calendars (gregorian, julian, astronomical; with convertdate, also: iso week, hebrew, islamic, french republican)

YMD = namedtuple('YMD', ['year', 'month', 'day'])

class InvalidDate(ValueError):
    pass

class Calendar(object):
    """Abstract base class for calendars. Supports YMD-type dates with weekdays.
    Converts to and from a date ordinal, where 1 is 1st January AD1 in proleptic Gregorian.
    Default implementations assume 1-based months and days and 0-based weekdays internally.
    """
    __metaclass__ = ABC.ABCMeta
    
    WEEKDAYS = ("Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday")
    
    # Formatting
    @property
    @ABC.abstractmethod
    def calendar_name(self):
        """Calendar name"""
    
    def day_name(self, ymd):
        """User-friendly formatting of day."""
        return str(ymd.day)
        
    def month_name(self, ymd):
        """User-friendly formatting of month."""
        return self.MONTHS[ymd.month-1]

    def year_name(self, ymd):
        """User-friendly formatting of year."""
        return str(ymd.year)
        
    def weekday_name(self, weekday):
        """User-friendly formatting of week day."""
        return self.WEEKDAYS[weekday]
        
    def date_name(self, ymd):
        """Optional user-friendly description of precise date."""
        return "?"
        
    def date_format(self, ymd, weekday, format_string="{W}, {D} {M} {Y}"):
        """User-friendly formatting of a full date, used in repr."""
        return format_string.format(W=self.weekday_name(weekday), D=self.day_name(ymd), M=self.month_name(ymd), Y=self.year_name(ymd), N=self.date_name(ymd), d=ymd.day, m=ymd.month, y=ymd.year)
    
    # Representation
    @ABC.abstractmethod
    def days_in_month(self, year, month): 
        """Number of days in a given month."""

    @ABC.abstractmethod
    def months_in_year(self, year): 
        """Number of months in a given year."""

    def validate(self, ymd):
        """Whether a given YMD representation is valid."""
        return ((1 <= ymd.month <= self.months_in_year(ymd.year)) and
                (1 <= ymd.day <= self.days_in_month(ymd.year, ymd.month)))
        
    @ABC.abstractmethod
    def date_to_ordinal(self, ymd):
        """Convert YMD to day ordinal."""
        
    @ABC.abstractmethod
    def ordinal_to_date(self, ordinal):
        """Convert day ordinal to YMD tuple."""
    
    def weekday(self, ymd, ordinal):
        """Week day for a given date."""
        # default to the standard 7-day week
        return ordinal % len(self.WEEKDAYS)
        
    # Calculations
    def carry_over(self, ymd):
        """Carry over invalid dates: e.g. Feb 30 > Mar 2."""
        year, month, day = ymd
        while month > self.months_in_year(year):
            month -= self.months_in_year(year)
            year += 1
        while month < 0:
            month += self.months_in_year(year-1)
            year -= 1
        if day > self.days_in_month(year, month):
            day, month = day - self.days_in_month(year, month), month + 1
        if month > self.months_in_year(year):
            year, month = year + 1, 1
        return YMD(year, month, day)        
        
    def add_years(self, ymd, year_delta):
        """Add years to YMD tuple."""
        return self.carry_over(YMD(ymd.year + year_delta, ymd.month, ymd.day))
        
    def add_months(self, ymd, month_delta):
        """Add months to YMD tuple."""
        return self.carry_over(YMD(ymd.year, ymd.month + month_delta, ymd.day))
        
    def add_days(self, ymd, day_delta):
        """Add days to YMD tuple."""
        return self.ordinal_to_date(self.date_to_ordinal(ymd) + day_delta)

class DerivedCalendar(Calendar):
    """Derived calendar that uses another calendar for its internal representation.
    Used for zero-less era calendars and the civil Hebrew calendar."""
    
    def __init__(self, base_calendar, to_base, from_base, calendar_name=None, **overrides):
        self.calendar = base_calendar
        self.name = self.calendar.calendar_name if calendar_name is None else calendar_name
        self.to_base = partial(to_base, self)
        self.from_base = partial(from_base, self)
        for k,v in overrides.items():
            setattr(self, k, partial(v, self))
    
    @property
    def calendar_name(self):
        return self.name
    
    def day_name(self, ymd):
        return self.calendar.day_name(self.to_base(ymd))
        
    def month_name(self, ymd):
        return self.calendar.month_name(self.to_base(ymd))

    def year_name(self, ymd):
        return self.calendar.year_name(self.to_base(ymd))
        
    def weekday_name(self, weekday):
        return self.calendar.weekday_name(weekday)
        
    def date_name(self, ymd):
        return self.calendar.date_name(self.to_base(ymd))
        
    def days_in_month(self, year, month): 
        return self.calendar.days_in_month(*(self.to_base(YMD(year, month, 1))[0:2]))

    def months_in_year(self, year): 
        return self.calendar.months_in_year(*(self.to_base(YMD(year, 1, 1))[0:1]))
        
    def validate(self, ymd):
        try:
            return self.calendar.validate(self.to_base(ymd))
        except InvalidDate:
            return False
        
    def date_to_ordinal(self, ymd):
        return self.calendar.date_to_ordinal(self.to_base(ymd))
        
    def ordinal_to_date(self, ordinal):
        return self.from_base(self.calendar.ordinal_to_date(ordinal))
    
    def weekday(self, ymd, ordinal):
        return self.calendar.weekday(self.to_base(ymd), ordinal)
    
    def add_years(self, ymd, year_delta):
        return self.from_base(self.calendar.add_years(self.to_base(ymd), year_delta))
        
    def add_months(self, ymd, month_delta):
        return self.from_base(self.calendar.add_months(self.to_base(ymd), month_delta))
        
    def add_days(self, ymd, day_delta):
        return self.from_base(self.calendar.add_days(self.to_base(ymd), day_delta))

# Calendar classes

class WesternCalendar(Calendar):
    """Proleptic Western calendar that includes year 0."""

    MONTHS = ("January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December")
    
    def __init__(self, julian=False):
        self.gregorian = not julian
        
    @property
    def calendar_name(self):
        return "astronomical {}".format("Gregorian" if self.gregorian else "Julian")

    def year_name(self, ymd):
        return str(ymd.year)
        
    def days_in_month(self, year, month): 
        if month == 2: return 28 + int(year % 4 == 0) - int(self.gregorian and year % 100 == 0 and year % 400 != 0)
        elif month in [4,6,9,11]: return 30
        else: return 31
        
    def months_in_year(self, year):
        return 12
        
    def date_to_ordinal(self, ymd):
        # based on years and months since 1 March BC1
        y = ymd.year - int(ymd.month <= 2) 
        m = ymd.month + 12 * int(ymd.month <= 2) - 3 
        d = ymd.day + (153 * m + 2) // 5 + 365 * y + y // 4 - 306
        return d - y // 100 + y // 400 if self.gregorian else d - 2
        
    def ordinal_to_date(self, ordinal):
        # see http://www.tondering.dk/claus/cal/julperiod.php
        a = ordinal + 305
        b = (4 * a + 3) // 146097 if self.gregorian else 0
        c = a - (146097 * b) // 4 if self.gregorian else ordinal + 305 + 2
        d = (4 * c + 3) // 1461
        e = c - (1461 * d) // 4
        m = (5 * e + 2) // 153
        day = e - (153 * m + 2) // 5 + 1
        month = m + 3 - 12 * (m // 10)
        year = 100 * b + d + m // 10
        return YMD(year, month, day)
        
def _era_to_astronomical(self, ymd):
    if ymd.year == 0:
        raise InvalidDate("{} does not have a year 0.".format(self.calendar_name))
    elif ymd.year < 0:
        return YMD(ymd.year + 1, ymd.month, ymd.day)
    else:
        return ymd
        
def _astronomical_to_era(self, ymd):
    return YMD(ymd.year - 1, ymd.month, ymd.day) if ymd.year <= 0 else ymd

def _era_year_name(self, ymd, bc=" BC", ad=""):
    return str(abs(ymd.year)) + (bc if (ymd.year < 0) else ad)

class IslamicCalendar(Calendar):
    """Proleptic Islamic Calendar that includes year 0."""
    
    MONTHS = ("Muharram", "Safar", "Rabi' al-awwal", "Rabi' al-Thani", "Jumada al-awwal", "Jumada al-Thani", "Rajab", "Sha'ban", "Ramadan", "Shawwal", "Dhu al-Qidah", "Dhu al-Hijjah")
        
    @property
    def calendar_name(self):
        return "Islamic"

    def days_in_month(self, year, month): 
        return cdate.islamic.month_length(year, month)
        
    def months_in_year(self, year):
        return 12
        
    def date_to_ordinal(self, ymd):
        return floor(cdate.islamic.to_jd(*ymd) - 1721424)
    
    def ordinal_to_date(self, ordinal):
        return YMD(*cdate.islamic.from_jd(ordinal + 1721424))
        
class HebrewCalendar(Calendar):
    """Proleptic Hebrew Calendar. Months are based on the ecclesiastical year, years on the civil year. 
    This means that the year increments between months 6 and 7!"""
    
    MONTHS = ("Nisan", "Iyar", "Sivan", "Tammuz", "Abh", "Elul", "Tishri", "Marcheshvan", "Kislev", "Tebheth", "Shebhat", "Adar", "Adar A", "Adar B")
        
    @property
    def calendar_name(self):
        return "Hebrew"

    def month_name(self, ymd):
        return self.MONTHS[ymd.month - 1 + int(ymd.month >= 12 and self.months_in_year(ymd.year) == 13)]
        
    def days_in_month(self, year, month): 
        return cdate.hebrew.month_days(year, month)
        
    def months_in_year(self, year):
        return cdate.hebrew.year_months(year)
        
    def date_to_ordinal(self, ymd):
        return floor(cdate.hebrew.to_jd(*ymd) - 1721424)
    
    def ordinal_to_date(self, ordinal):
        return YMD(*cdate.hebrew.from_jd(ordinal + 1721424))
        
    def add_months(self, ymd, month_delta):
        raise NotImplementedError("Date deltas not supported for ecclesiastical Hebrew calendar.")

    def add_years(self, ymd, year_delta):
        raise NotImplementedError("Date deltas not supported for ecclesiastical Hebrew calendar.")

def _ecclesiastical_to_civil(self, ymd):
    if ymd.month >= 7:
        month = ymd.month - 6
    else:
        month = ymd.month + 6 + int(self.calendar.months_in_year(ymd.year) == 13)
    return YMD(ymd.year, month, ymd.day)
    
def _civil_to_ecclesiastical(self, ymd):
    if ymd.month <= 6 + int(self.calendar.months_in_year(ymd.year) == 13):
        month = ymd.month + 6
    else:
        month = ymd.month - 6 - int(self.calendar.months_in_year(ymd.year) == 13)
    return YMD(ymd.year, month, ymd.day)

def _hebrew_add_years(self, ymd, year_delta):
    year, month, day = ymd
    year += year_delta
    if self.months_in_year(year) > self.months_in_year(ymd.year) and month >= 6:
        month += 1 # skip past Adar A
    elif self.months_in_year(year) < self.months_in_year(ymd.year) and month >= 7:
        month -= 1 # no Adar A
    return self.carry_over(YMD(year, month, day))
    
class RepublicanCalendar(Calendar):
    """Proleptic French Republican Calendar"""
    
    WEEKDAYS = ("Primidi", "Duodi", "Tridi", "Quartidi", "Quintidi", "Sextidi", "Septidi", "Octidi", "Nonidi", "Décadi")
    
    MONTHS = ("Vendémiaire", "Brumaire", "Frimaire", "Nivôse", "Pluviôse", "Ventôse", "Germinal", "Floréal", "Prairial", "Messidor", "Thermidor", "Fructidor", "Sansculottides")
        
    @property
    def calendar_name(self):
        return "French Republican"

    def date_name(self, ymd):
        return cdate.french_republican.french_republican_days[ymd.month][ymd.day-1]
        
    def date_format(self, ymd, weekday, format_string=None):
        if format_string is None:
            format_string = "{W}, {D} {M} {Y} ({N})" if ymd.month <= 12 else "{N}, {M} {Y}"
        return super().date_format(ymd, weekday, format_string)
    
    def days_in_month(self, year, month): 
        return 30 if month <= 12 else 5 + int(cdate.french_republican.leap(year))
        
    def months_in_year(self, year):
        return 13
        
    def weekday(self, ymd, ordinal):
        return (ymd.day - 1) % len(self.WEEKDAYS)

    def date_to_ordinal(self, ymd):
        return floor(cdate.french_republican.to_jd(*ymd) - 1721424)
    
    def ordinal_to_date(self, ordinal):
        return YMD(*[int(x) for x in cdate.french_republican.from_jd(ordinal + 1721424)])
        
    def add_months(self, ymd, month_delta):
        # skip complementary month unless we start there
        extra_months = 0 if ymd.month == 13 else (ymd.month + month_delta) // 13
        return self.carry_over(YMD(ymd.year, ymd.month + month_delta + extra_months, ymd.day))
    
class ISOCalendar(Calendar):
    """ISO week date"""
    
    @property
    def calendar_name(self):
        return "ISO week"
        
    def month_name(self, ymd):
        return "W{:02d}".format(ymd.month)

    def date_format(self, ymd, weekday, format_string="{W}, {Y}-{M}-{D}"):
        return super().date_format(ymd, weekday, format_string)
        
    def days_in_month(self, year, month):
        return 7

    def months_in_year(self, year): 
        return cdate.iso.weeks_per_year(year)

    def date_to_ordinal(self, ymd):
        return floor(cdate.iso.to_jd(*ymd) - 1721425)
    
    def ordinal_to_date(self, ordinal):
        return YMD(*[int(x) for x in cdate.iso.from_jd(ordinal + 1721425)])

# Calendars
   
isodate = WesternCalendar()
isoweek = ISOCalendar()
gregorian = DerivedCalendar(WesternCalendar(), _era_to_astronomical, _astronomical_to_era, "Gregorian", year_name=_era_year_name)
julian = DerivedCalendar(WesternCalendar(julian=True), _era_to_astronomical, _astronomical_to_era, "Julian", year_name=_era_year_name)
islamic = DerivedCalendar(IslamicCalendar(), _era_to_astronomical, _astronomical_to_era, year_name=partial(_era_year_name, ad=" AH", bc=" BH"))
hebrew = DerivedCalendar(HebrewCalendar(), _civil_to_ecclesiastical, _ecclesiastical_to_civil, add_months=Calendar.add_months, add_years=_hebrew_add_years)
republican = RepublicanCalendar()

# Dates

@total_ordering
class Date(object):

    def __init__(self, date=None, calendar=gregorian, format=None):
        self.calendar = calendar
        if date is None:
            self.ordinal = datetime.date.today().toordinal()
            self.ymd = calendar.ordinal_to_date(self.ordinal)
        elif isinstance(date, Date):
            self.ordinal = date.ordinal
            self.ymd = calendar.ordinal_to_date(self.ordinal)
        elif isinstance(date, datetime.date):
            self.ordinal = date.toordinal()
            self.ymd = calendar.ordinal_to_date(self.ordinal)
        elif isinstance(date, Integral):
            self.ordinal = int(date)
            self.ymd = calendar.ordinal_to_date(self.ordinal)
        elif non_string_sequence(date, Integral) and len(date) == 3:
            self.ymd = YMD(*date)
            if not calendar.validate(self.ymd):
                raise InvalidDate("Invalid {} date: {}".format(calendar.calendar_name, self.ymd))
            self.ordinal = calendar.date_to_ordinal(self.ymd)
        else:
            raise TypeError("Invalid input type for Date")
        self.weekday = calendar.weekday(self.ymd, self.ordinal)
        self.format = format
            
    def __repr__(self):
        date_string = self.calendar.date_format(self.ymd, self.weekday, *([self.format] if self.format else []))
        return "{} [{}]".format(date_string, self.calendar.calendar_name)
    
    def date_format(self, format_string):
        return self.calendar.date_format(self.ymd, self.weekday, format_string)
        
    def __hash__(self):
        return hash(str(self.ordinal))
        
    def __eq__(self, other):
        if isinstance(other, Date):
            return self.ordinal == other.ordinal
        else:
            return NotImplemented
            
    def __lt__(self, other):
        if isinstance(other, Date):
            return self.ordinal < other.ordinal
        else:
            return NotImplemented
            
    def __add__(self, other):
        if isinstance(other, Integral):
            return Date(self.ordinal + int(other), calendar=self.calendar, format=self.format)
        else:
            return NotImplemented

    def __sub__(self, other):
        if isinstance(other, Date):
            return self.ordinal - other.ordinal
        elif isinstance(other, Integral):
            return Date(self.ordinal - int(other), calendar=self.calendar, format=self.format)
        else:
            return NotImplemented
            
    def to_calendar(self, calendar=None, format=None):
        return Date(self, calendar=calendar or self.calendar, format=format)
        
    def to_date(self, calendar=gregorian):
        return datetime.date.fromordinal(self.ordinal)

# Date deltas

class DateDelta(object):

    """Abstract base class for date deltas."""
    __metaclass__ = ABC.ABCMeta
    
    @ABC.abstractmethod
    def add_delta(self, date):
        """Add delta to a Date."""
        
    @ABC.abstractmethod
    def subtract_delta(self, date):
        """Subtract delta from a Date."""

    # apply delta to date
    def __radd__(self, other):
        if isinstance(other, Date):
            return self.add_delta(other)
        elif isinstance(other, datetime.date):
            return self.add_delta(Date(other)).to_date()
        else:
            return NotImplemented

    def __rsub__(self, other):
        if isinstance(other, Date):
            return self.subtract_delta(other)
        elif isinstance(other, datetime.date):
            return self.subtract_delta(Date(other)).to_date()
        else:
            return NotImplemented

    # combine deltas
    def __neg__(self):
        return DateDeltaNegate(self)
    
    def __add__(self, other):
        if issubclass(type(other), DateDelta):
            return DateDeltaAdd(self, other)
        else:
            return NotImplemented

    def __sub__(self, other):
        if issubclass(type(other), DateDelta):
            return DateDeltaAdd(self, DateDeltaNegate(other))
        else:
            return NotImplemented
            
    def __mul__(self, other):
        if isinstance(other, int):
            if other >= 0:
                return DateDeltaAdd(*([self] * other))
            else:
                return DateDeltaAdd(*([-self] * -other))
        else:
            return NotImplemented

class DateDeltaNegate(DateDelta):

    def __init__(self, datedelta):
        self.delta = datedelta
        
    def __repr__(self):
        return "-{}".format(self.delta)
        
    def add_delta(self, date):
        return self.delta.subtract_delta(date)
        
    def subtract_delta(self, date):
        return self.delta.add_delta(date)
    
class DateDeltaAdd(DateDelta):

    def __init__(self, *datedeltas):
        self.deltas = datedeltas
        
    def __repr__(self):
        repr = ""
        for i,delta in enumerate(self.deltas):
            if i == 0:
                repr += str(delta)
            elif isinstance(delta, DateDeltaNegate):
                repr += " - " + str(delta.delta)
            else:
                repr += " + " + str(delta)
        return "({})".format(repr)
        
    def add_delta(self, date):
        return reduce(lambda date,delta: delta.add_delta(date), self.deltas, date)
        
    def subtract_delta(self, date):
        return reduce(lambda date,delta: delta.subtract_delta(date), self.deltas, date)

class DateInterval(DateDelta):

    def __init__(self, years=0, months=0, days=0):
        self.years = years
        self.months = months
        self.days = days
        
    @classmethod
    def from_dates(cls, start, end, calendar=gregorian):
        start = Date(start, calendar=calendar)
        end = Date(end, calendar=calendar)
        if end < start:
            return -DateInterval.from_dates(end, start, calendar)
        years, months, days = 0, 0, 0
        current = start
        while Date(calendar.add_years(current.ymd, years + 1), calendar) <= end:
            years += 1
        current = Date(calendar.add_years(current.ymd, years), calendar)
        while Date(calendar.add_months(current.ymd, months + 1), calendar) <= end:
            months += 1
        current = Date(calendar.add_months(current.ymd, months), calendar)
        days = end - current
        return cls(years, months, days)
        
    def __repr__(self):
        attrs = ["{}={}".format(v,getattr(self,v)) for v in ("years","months","days") if getattr(self,v)!=0]
        return "DateInterval({})".format(",".join(attrs))

    def add_delta(self, date):
        ymd = date.ymd
        ymd = date.calendar.add_years(ymd, self.years)
        ymd = date.calendar.add_months(ymd, self.months)
        ymd = date.calendar.add_days(ymd, self.days)
        return Date(ymd, calendar=date.calendar, format=date.format)
        
    def subtract_delta(self, date):
        ymd = date.ymd
        ymd = date.calendar.add_years(ymd, -self.years)
        ymd = date.calendar.add_months(ymd, -self.months)
        ymd = date.calendar.add_days(ymd, -self.days)
        return Date(ymd, calendar=date.calendar, format=date.format)

class DateFilter(DateDelta):

    def __init__(self, filter_fn, max_date=None, min_date=None):
        self.filter = filter_fn
        self.max_date = None if max_date is None else Date(max_date)
        self.min_date = None if min_date is None else Date(min_date)
        
    def __repr__(self):
        return "DateFilter({})".format(self.filter)

    def add_delta(self, date):
        while self.max_date is None or date < self.max_date:
            date = Date(date.ordinal + 1, calendar=date.calendar, format=date.format)
            if self.filter(date):
                return date
        raise ValueError("Date out of bounds")
        
    def subtract_delta(self, date):
        while self.max_date is None or date > self.min_date:
            date = Date(date.ordinal - 1, calendar=date.calendar, format=date.format)
            if self.filter(date):
                return date
        raise ValueError("Date out of bounds")
        
# Date ranges

class DateRange(collections.abc.Sequence):

    def __init__(self, start, end, calendar=gregorian, format=None):
        self.start = Date(start, calendar=calendar, format=format)
        self.end = Date(end, calendar=calendar, format=format)
        if self.start > self.end:
            raise ValueError("Start date later than end date")
        self.calendar = calendar
        self.format = format
    
    def range_format(self, format_string):
        return format_string.format(
                D1=self.calendar.day_name(self.start.ymd),
                M1=self.calendar.month_name(self.start.ymd),
                Y1=self.calendar.year_name(self.start.ymd),
                W1=self.calendar.weekday_name(self.start.weekday),
                N1=self.calendar.date_name(self.start.ymd),
                d1=self.start.ymd.day,
                m1=self.start.ymd.month,
                y1=self.start.ymd.year,
                D2=self.calendar.day_name(self.end.ymd),
                M2=self.calendar.month_name(self.end.ymd),
                Y2=self.calendar.year_name(self.end.ymd),
                W2=self.calendar.weekday_name(self.end.weekday),
                N2=self.calendar.date_name(self.end.ymd),
                d2=self.end.ymd.day,
                m2=self.end.ymd.month,
                y2=self.end.ymd.year)
    
    def __repr__(self):
        if self.format is not None:
            format_string = self.format
        elif self.start.ymd.year != self.end.ymd.year:
            format_string = "{D1} {M1} {Y1} - {D2} {M2} {Y2}"
        elif self.start.ymd.month != self.end.ymd.month:
            format_string = "{D1} {M1}-{D2} {M2} {Y2}"
        elif self.start.ymd.day != self.end.ymd.day:
            format_string = "{D1}-{D2} {M2} {Y2}"
        else:
            format_string = "{D2} {M2} {Y2}"
        return "{} [{}]".format(self.range_format(format_string), self.calendar.calendar_name)
        
    def __eq__(self, other):
        if isinstance(other, DateRange):
            return self.start == other.start and self.end == other.end
        elif isinstance(other, Date):
            return self == DateRange(other, other)
        else:
            return NotImplemented
            
    def __lt__(self, other):
        if isinstance(other, DateRange):
            return self.end < other.start
        elif isinstance(other, Date):
            return self < DateRange(other, other)
        else:
            return NotImplemented

    def __le__(self, other):
        if isinstance(other, DateRange):
            return self.end <= other.start
        elif isinstance(other, Date):
            return self <= DateRange(other, other)
        else:
            return NotImplemented
            
    def __gt__(self, other):
        if isinstance(other, DateRange):
            return self.start > other.end
        elif isinstance(other, Date):
            return self > DateRange(other, other)
        else:
            return NotImplemented

    def __ge__(self, other):
        if isinstance(other, DateRange):
            return self.start >= other.end
        elif isinstance(other, Date):
            return self >= DateRange(other, other)
        else:
            return NotImplemented
            
    def __contains__(self, other):
        if isinstance(other, DateRange):
            return self.start <= other.start <= other.end <= self.end
        elif isinstance(other, Date):
            return DateRange(other, other) in self
        else:
            return False

    def __len__(self):
        return self.end - self.start + 1
        
    def __getitem__(self, key):
        if not isinstance(key, Integral):
            raise TypeError
        date = self.start + key
        if not self.start <= date <= self.end:
            raise IndexError
        return date
        
    def __add__(self, other):
        if not non_string_sequence(other):
            other = (other, other)
        elif not len(other) == 2:
            raise NotImplemented
        return DateRange(self.start + other[0], self.end + other[1], calendar=self.calendar, format=self.format)
         
    def __sub__(self, other):
        if isinstance(other, DateRange):
            other = (other.start, other.end)
        elif not non_string_sequence(other):
            other = (other, other)
        elif not len(other) == 2:
            raise NotImplemented
        difference = (self.start - other[0], self.end - other[1])
        if non_string_sequence(difference, Date):
            return DateRange(difference[0], difference[1], calendar=self.calendar, format=self.format)
        else:
            return difference
         
    def to_calendar(self, calendar=None, format=None):
        return DateRange(self.start, self.end, calendar=calendar or self.calendar, format=format)

class DatePrecision(Enum):
    """Date precisions."""
    DAY, MONTH, YEAR, DECADE, CENTURY, MILLENNIUM = range(6)

                
class ApproximateDate(DateRange):

    CIRCA_RANGE = 2

    def __init__(self, date, precision, circa=False, calendar=gregorian):
    
        if isinstance(date, Integral):
            date = (date,)  # interpret numbers as years, not ordinals
        if non_string_sequence(date, Integral) and len(date) == 1:
            date = (date[0], calendar.months_in_year(date[0]) // 2 + 1, 1)
        elif non_string_sequence(date, Integral) and len(date) == 2:
            date = (date[0], date[1], calendar.days_in_month(date[0], date[1]) // 2 + 1)
        self.base_date = Date(date, calendar=calendar)
        self.precision = precision
        self.description = None
        self.circa = circa
        
        # initialise range
        year, month, day = self.base_date.ymd
        circa_range = self.CIRCA_RANGE * int(circa)
        if precision == DatePrecision.DAY:
            delta = DateInterval(days=circa_range)
            start = self.base_date-delta
            end = self.base_date+delta
        elif precision == DatePrecision.MONTH:
            delta = DateInterval(months=circa_range)
            start = Date((year, month, 1), calendar=calendar) - delta
            end = Date((year, month, calendar.days_in_month(year, month)), calendar=calendar) + delta
        elif precision == DatePrecision.YEAR:
            delta = DateInterval(years=circa_range)
            last_month = calendar.months_in_year(year)
            start = Date((year, 1, 1), calendar=calendar) - delta
            end = Date((year, last_month, calendar.days_in_month(year, last_month)), calendar=calendar) + delta
        elif precision in (DatePrecision.DECADE, DatePrecision.CENTURY, DatePrecision.MILLENNIUM):
            n = (None, DatePrecision.DECADE, DatePrecision.CENTURY, DatePrecision.MILLENNIUM).index(precision)
            delta = DateInterval(years=circa_range * 10**n)
            first_year = year - year % 10**n if year >= 0 else (year-1) - (year-1) % 10**n + 1
            if not calendar.validate(YMD(first_year, 1, 1)): first_year += 1 # hack for missing year 0
            last_year = first_year + 10**n - 1 - int(first_year == -10**n + 1) # count 0 as positive only
            last_month = calendar.months_in_year(last_year)
            last_day = calendar.days_in_month(last_year, last_month)
            start = Date((first_year, 1, 1), calendar=calendar) - delta
            end = Date((last_year, last_month, last_day), calendar=calendar) + delta
            self.description = "{}{}s".format(abs(year) // 10**n, "0"*n)
        else:
            raise NotImplemented
        super().__init__(start, end, calendar=calendar)

    def __repr__(self):
        if self.precision == DatePrecision.DAY:
            range = self.base_date.date_format("{D} {M} {Y}")
        elif self.precision == DatePrecision.MONTH:
            range = self.base_date.date_format("{M} {Y}")
        elif self.precision == DatePrecision.YEAR:        
            range = self.base_date.date_format("{Y}")
        elif self.precision in (DatePrecision.DECADE, DatePrecision.CENTURY, DatePrecision.MILLENNIUM):
            range = self.base_date.date_format("{Y}").replace(str(abs(self.base_date.ymd.year)), self.description)
        else:
            raise NotImplemented
        return "{}{} ({}) [{}]".format("c. "*int(self.circa), range, self.precision.name.lower(), self.calendar.calendar_name)
