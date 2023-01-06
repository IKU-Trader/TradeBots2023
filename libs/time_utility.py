# -*- coding: utf-8 -*-
"""
Created on Sun Dec  4 22:37:16 2022

@author: IKU-Trader
"""

import datetime
import calendar
import pytz

#TIMEZONE_TOKYO = datetime.timezone(datetime.timedelta(hours=+9), 'Asia/Tokyo')
TIMEZONE_TOKYO = pytz.timezone('Asia/Tokyo')

def changeTimezone(pytime_array: [datetime.datetime], tzinfo):
    out =[]
    for i in range(len(pytime_array)):
        t = pytime_array[i].astimezone(tzinfo)
        out.append(t)
    return out

def sliceTime(pytime_array: list, time_from, time_to):
    begin = None
    end = None
    for i in range(len(pytime_array)):
        t = pytime_array[i]
        if begin is None:
            if t >= time_from:
                begin = i
        else:
            if t > time_to:
                end = i
                return (end - begin + 1, begin, end)
    if begin is not None:
        end = len(pytime_array) - 1
        length = end -begin + 1
        return (length, begin, end)
    else:
        return (0, None, None)
    
def str2pytimeArray(time_str_array: [str], tzinfo, form='%Y-%m-%d %H:%M:%S'):
    out = []
    for s in time_str_array:
        i = s.find('+')
        if i > 0:
            s = s[:i]
        t = datetime.datetime.strptime(s, form)
        t = pyTime(t.year, t.month, t.day, t.hour, t.minute, t.second, tzinfo)
        out.append(t)
    return out

def dayOfLastSunday(year, month):
    '''dow: Monday(0) - Sunday(6)'''
    dow = 6
    n = calendar.monthrange(year, month)[1]
    l = range(n - 6, n + 1)
    w = calendar.weekday(year, month, l[0])
    w_l = [i % 7 for i in range(w, w + 7)]
    return l[w_l.index(dow)]  

def utcTime(year, month, day, hour, minute, second):
    return pyTime(year, month, day, hour, minute, second, pytz.timezone('UTC'))   

#https://pytz.sourceforge.net/
#Unfortunately using the tzinfo argument of the standard datetime constructors ‘’does not work’’ with pytz for many timezones.
def pyTime(year, month, day, hour, minute, second, tzinfo):
    t = datetime.datetime(year, month, day, hour, minute, second)
    time = tzinfo.localize(t)
    return time

def isSummerTime(date_time):
    day0 = dayOfLastSunday(date_time.year, 3)
    tsummer0 = utcTime(date_time.year, 3, day0, 0, 0)
    day1 = dayOfLastSunday(date_time.year, 10)
    tsummer1 = utcTime(date_time.year, 10, day1, 0, 0)
    if date_time > tsummer0 and date_time < tsummer1:
        return True
    else:
        return False