# -*- coding: utf-8 -*-
"""
Created on Tue Jan  3 16:26:45 2023

@author: IKU-Trader
"""
import os
import sys
sys.path.append("./PyCandleChart")
sys.path.append("./TA")

import pandas as pd
import glob
import pytz
from time_utility import changeTimezone, TIMEZONE_TOKYO, str2pytimeArray, sliceTime, pyTime
from datetime import datetime, timedelta

TimeUnit = str
UNIT_MINUTE:TimeUnit = 'MINUTE'
UNIT_HOUR:TimeUnit = 'HOUR'
UNIT_DAY:TimeUnit = 'DAY'


def fileList(dir_path, extension):
    path = os.path.join(dir_path, '*.' + extension)
    l = glob.glob(path)
    return l

def sortIndex(array:[]):
    index = [pair[0] for pair in sorted(enumerate(array), key=lambda x:x[1])]
    return index
       
def sortWithIndex(array:[], index:[]):
    if len(array) != len(index):
        return None
    out = [array[i] for i in index]
    return out

# -----
    
class DataServerStub:
    def __init__(self, name:str, interval:int, time_unit:TimeUnit):
        self.name = name
        self.interval = interval
        self.time_unit = time_unit
        pass
    
    """
    def candles2tohlcv(self, candles):
        if len(candles) == 0:
            return []
        n = len(candles[0])
        arrays = []
        for i in range(n):
            array = []
            for candle in candles:
                array.append(candle[i])
            arrays.append(array)
        return arrays

    def tohlcv2Candles(self, tohlc_arrays):
        out = []
        n = len(tohlc_arrays)
        size = len(tohlc_arrays[0])
        for i in range(size):
            v = []
            for j in range(n):
                v.append(tohlc_arrays[j][i])
            out.append(v)
        return out   
    """ 
  
    def merge(self, tohlcv, new_tohlcv):
        if tohlcv is None:
            tohlcv = new_tohlcv
            return tohlcv
        for old, new in zip(tohlcv, new_tohlcv):
            old += new
        return tohlcv
    
    def parseTime(self, tohlcv:[]):
        time = str2pytimeArray(tohlcv[0], pytz.utc)
        jst = changeTimezone(time, TIMEZONE_TOKYO)
        index = sortIndex(jst)        
        jst = sortWithIndex(jst, index)
        out = [jst]
        for i in range(1, len(tohlcv)):
            d = sortWithIndex(tohlcv[i], index)
            out.append(d)
        return out
    
    def roundTime(self, time: datetime, interval: int, unit: TimeUnit):
        zone = time.tzinfo
        if unit == UNIT_MINUTE:
            t = datetime(time.year, time.month, time.day, time.hour, 0, 0, tzinfo=zone)
        elif unit == UNIT_HOUR:
            t = datetime(time.year, time.month, time.day, 0, 0, 0, tzinfo=zone)
        elif unit == UNIT_DAY:
            t = datetime(time.year, time.month, time.day, 0, 0, 0, tzinfo=zone)
            return t
        if t == time:
            return t
        while t < time:
            if unit == UNIT_MINUTE:
                t += timedelta(minutes=interval)
            elif unit == UNIT_HOUR:
                t += timedelta(hours=interval)
        return t
    
    def candlePrice(self, time:[datetime], ohlcv_list:[]):
        m = len(ohlcv_list[0])
        n = len(ohlcv_list)
        o = ohlcv_list[0][0]
        c = ohlcv_list[-1][3]
        h_array = [ohlcv_list[i][1] for i in range(n)]
        h = max(h_array)
        l_array = [ohlcv_list[i][2] for i in range(n)]
        l = min(l_array)
        if m > 4:
            v_array = [ohlcv_list[i][4] for i in range(n)]
            v = sum(v_array)
            return [time, o, h, l, c, v]
        else:
            return [time, o, h, l, c]
    
    def resample(self, tohlcv, interval, unit):        
        time = tohlcv[0]
        n = len(time)
        op = tohlcv[1]
        hi = tohlcv[2]
        lo = tohlcv[3]
        cl = tohlcv[4]
        if len(tohlcv) > 5:
            vo = tohlcv[5]
            is_volume = True
        else:
            is_volume = False
        data_list = None
        candles = []
        current_time = None
        for i in range(n):
            t_round = self.roundTime(time[i], interval, unit)
            if is_volume:
                values = [op[i], hi[i], lo[i], cl[i], vo[i]]
            else:
                values = [op[i], hi[i], lo[i], cl[i]]
            if current_time is None:
                current_time = t_round
                data_list = [values]
            else:
                if t_round == current_time:
                    data_list.append(values)
                else:
                    candle = self.candlePrice(current_time, data_list)
                    candles.append(candle)
                    data_list = [values]
                    current_time = t_round
        return self.toTohlcv(candles)

    def importFiles(self, dir_path):
        tohlcv = None  
        for file in fileList(dir_path, 'csv'):
            df = pd.read_csv(file)
            data = self.toTohlcv(df.values)
            tohlcv = self.merge(tohlcv, data)
        tohlcv = self.parseTime(tohlcv)
        self.tohlcv = self.resample(tohlcv, self.interval, self.time_unit)
        
    def importFile(self, file_path):
        df = pd.read_csv(file_path)
        tohlcv = self.toTohlcv(df.values)
        tohlcv = self.parseTime(tohlcv)
        self.tohlcv = self.resample(tohlcv, self.interval, self.time_unit)
        
    def getTohlcv(self, time_from=None, time_to=None):
        if time_from is None and time_to is None:
            return self.tohlcv
        if time_from is None:
            time_from = self.tohlcv[0][0]
        if time_to is None:
            time_to = self.tohlcv[0][-1]
        length, begin, end = sliceTime(self.tohlcv[0], time_from, time_to)
        if length <= 0:
            return []
        out = []
        for i in range(len(self.tohlcv)):
            out.append(self.tohlcv[i][begin: end + 1])
        return out
    
    def toCandles(self, tohlcv:[]):
        out = []
        n = len(tohlcv[0])
        for i in range(n):
            d = [array[i] for array in tohlcv]
            out.append(d)
        return out
    
    def toTohlcv(self, candles:[]):
        n = len(candles)
        m = len(candles[0])
        arrays = []
        for i in range(m):
            array = [candles[j][i] for j in range(n)]
            arrays.append(array)
        return arrays
    
    def getCandles(self, time_from=None, time_to=None):
        tohlcv = self.getTohlcv(time_from=time_from, time_to=time_to)
        if len(tohlcv) == 0:
            return []
        return self.toCandles(tohlcv)
# -----
        
def test():
    server = DataServerStub('DJI', 5, UNIT_MINUTE)
    server.importFile('./data/DJI_Feature_2019_08.csv')
    t0 = pyTime(2019, 8, 9, 0, 0, 0, TIMEZONE_TOKYO)
    t1 = pyTime(2019, 8, 10, 0, 0, 0, TIMEZONE_TOKYO)
    candles = server.getCandles()
    df = pd.DataFrame(data=candles, columns=['Time', 'Open', 'High', 'Low', 'Close', 'Volume'])
    df.to_csv('validation.csv', index=False)
    

def test2():
    t0 = datetime(2020, 1, 21)
    t1 = datetime(2020, 1, 8)
    t2 = datetime(2020, 1, 1)
    t3 = datetime(2020, 1, 3)
    index = sortIndex([t0, t1, t2, t3])
    d = [t0, t1, t2, t3]
    
    d2 = d[index]
    print(index)

if __name__ == '__main__':
    test()