# -*- coding: utf-8 -*-
"""
Created on Tue Nov 29 11:21:36 2022

@author: IKU-Trader
"""

import sys
sys.path.append('../')

import MetaTrader5 as mt5
from mt5_const import mt5_const as const
from TimeUtils import TimeUtils
from datetime import datetime
 
class PyMT5:
    def __init__(self, market):
        self.market = market
        if not mt5.initialize():
            print("initialize() failed")
            mt5.shutdown()
        print('Version: ', mt5.version())
    
    def close(self):
        mt5.shutdown()
    
    def convert(self, data):
        if data is None:
            return ([], {})
        timeJst = []
        timestamp = []
        arrays = []
        for i in range(5):
            arrays.append([])
        ohlcv = []
        for d in data:
            values = list(d)
            jst = TimeUtils.timestamp2jst(values[0])
            timeJst.append(jst)
            timestamp.append(jst.timestamp())
            for i in range(5):
                if i == 4:
                    j = 7
                else:
                    j = i + 1
                arrays[i].append(values[j])
            ohlcv.append([values[1], values[2], values[3], values[4]])
        dic = {}
        dic[const.TIMEJST] = timeJst
        dic[const.TIMESTAMP] = timestamp
        dic[const.OPEN] = arrays[0]
        dic[const.HIGH] = arrays[1]
        dic[const.LOW] = arrays[2]
        dic[const.CLOSE] = arrays[3]
        dic[const.VOLUME] = arrays[4]
        return (ohlcv, dic)
     
    def download(self, timeframe: str, size: int=99999):
        d = mt5.copy_rates_from_pos(self.market, const.TIMEFRAME[timeframe][0] , 0, size) 
        return self.convert(d)

    def downloadRange(self, timeframe: str, begin_jst: datetime, end_jst: datetime):
        utc_from = self.jst2serverTime(begin_jst)
        utc_to = self.jst2serverTime(end_jst)
        d = mt5.copy_rates_range(self.stock, const.TIMEFRAME[timeframe][0] , utc_from, utc_to) 
        return self.convert(d)
    
    def downloadTicks(self, timeframe: str, from_jst: datetime, size: int=100000):
        utc_from = self.jst2serverTime(from_jst)
        d = mt5.copy_ticks_from(self.stock, const.TIMEFRAME[timeframe][0] , utc_from, size, mt5.COPY_TICKS_ALL) 
        return self.convert(d)

# -----
    
def test(size):
    server = PyMT5('USDJPY')
    ohlcv, dic =  server.download('M1', size=size) 
    print(ohlcv)
    print(dic[const.TIMEJST])

if __name__ == "__main__":
    test(3)