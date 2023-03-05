# -*- coding: utf-8 -*-
"""
Created on Sun Dec  4 22:37:16 2022

@author: IKU-Trader
"""

import calendar
import pytz
from datetime import datetime, timezone, timedelta


class TimeUtils:

    TIMEZONE_TOKYO = pytz.timezone('Asia/Tokyo')

    @staticmethod
    def changeTimezone(pytime_array: [datetime], tzinfo):
        out =[]
        for i in range(len(pytime_array)):
            t = pytime_array[i].astimezone(tzinfo)
            out.append(t)
        return out
       
    @staticmethod
    def str2pytimeArray(time_str_array: [str], tzinfo, form='%Y-%m-%d %H:%M:%S'):
        out = []
        for s in time_str_array:
            i = s.find('+')
            if i > 0:
                s = s[:i]
            t = datetime.strptime(s, form)
            t = TimeUtils.pyTime(t.year, t.month, t.day, t.hour, t.minute, t.second, tzinfo)
            out.append(t)
        return out
    
    @staticmethod
    def dayOfLastSunday(year, month):
        '''dow: Monday(0) - Sunday(6)'''
        dow = 6
        n = calendar.monthrange(year, month)[1]
        l = range(n - 6, n + 1)
        w = calendar.weekday(year, month, l[0])
        w_l = [i % 7 for i in range(w, w + 7)]
        return l[w_l.index(dow)]  
    
    @staticmethod
    def utcTime(year, month, day, hour, minute, second):
        return TimeUtils.pyTime(year, month, day, hour, minute, second, pytz.timezone('UTC'))   
    
    #https://pytz.sourceforge.net/
    #Unfortunately using the tzinfo argument of the standard datetime constructors ‘’does not work’’ with pytz for many timezones.
    @staticmethod
    def pyTime(year, month, day, hour, minute, second, tzinfo):
        t = datetime(year, month, day, hour, minute, second)
        time = tzinfo.localize(t)
        return time
    
    @staticmethod
    def isSummerTime(date_time):
        day0 = TimeUtils.dayOfLastSunday(date_time.year, 3)
        tsummer0 = TimeUtils.utcTime(date_time.year, 3, day0, 0, 0, 0)
        day1 = TimeUtils.dayOfLastSunday(date_time.year, 10)
        tsummer1 = TimeUtils.utcTime(date_time.year, 10, day1, 0, 0, 0)
        if date_time > tsummer0 and date_time < tsummer1:
            return True
        else:
            return False
        
    @staticmethod
    def timestamp2jst(utc_server):
        t = datetime.fromtimestamp(utc_server, TimeUtils.TIMEZONE_TOKYO)
        if TimeUtils.isSummerTime(t):
            dt = 1
        else:
            dt = 2
        t -= timedelta(hours=dt)
        return t
    
    @staticmethod    
    def jst2timestamp(jst):
        timestamp = []
        for t in jst:
            timestamp.append(t.timestamp())
        return timestamp
    
    @staticmethod    
    def jst2utc(jst):
        utc = []
        for t in jst:
            utc.append(t.astimezone(timezone.utc))
        return utc
    
    @staticmethod        
    def numpyDateTime2pyDatetime(np_time):
        py_time = datetime.fromtimestamp(np_time.astype(datetime) * 1e-9)
        return py_time    