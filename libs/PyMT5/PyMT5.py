# -*- coding: utf-8 -*-
"""
Created on Tue Nov 29 11:21:36 2022

@author: IKU-Trader
"""

import sys
sys.path.append('../')

import pandas as pd
import MetaTrader5 as mt5
from mt5_const import mt5_const as const
from time_util import timestamp2jst
 
class PyMT5:
    def __init__(self, market):
        self.market = market
        if not mt5.initialize():
            print("initialize() failed")
            mt5.shutdown()
        #print('Version: ', mt5.version())
        pass
    
    def close(self):
        mt5.shutdown()
        pass
    
    def convert(self, data):
        if data is None:
            return [], [], {}
        
        timeJst = []
        timestamp = []
        o = []
        h = []
        l = []
        c = []
        v = []
        ohlcv = []
        for d in data:
            values = list(d)
            jst = timestamp2jst(values[0])
            timeJst.append(jst)
            timestamp.append(jst.timestamp())
            o.append(values[1])
            h.append(values[2])
            l.append(values[3])
            c.append(values[4])
            v.append(values[7])
            ohlcv.append([values[1], values[2], values[3], values[4]])
            
        dic = {}
        dic[const.TIMEJST] = timeJst
        dic[const.TIMESTAMP] = timestamp
        dic[const.OPEN] = o
        dic[const.HIGH] = h
        dic[const.LOW] = l
        dic[const.CLOSE] = c
        dic[const.VOLUME] = v
        return ohlcv, dic
     
    def download(self, timeframe:str, size:int=99999):
        d = mt5.copy_rates_from_pos(self.market, const.TIMEFRAME[timeframe][0] , 0, size) 
        ohlcv, dic = self.convert(d)
        return ohlcv, dic

    def downloadRange(self, timeframe, begin_jst, end_jst):
        utc_from = self.jst2serverTime(begin_jst)
        utc_to = self.jst2serverTime(end_jst)
        d = mt5.copy_rates_range(self.stock, const.TIMEFRAME[timeframe][0] , utc_from, utc_to) 
        data = self.convert2Array(d)
        return data
    
    def downloadTicks(self, timeframe, from_jst, size=100000):
        utc_from = self.jst2serverTime(from_jst)
        d = mt5.copy_ticks_from(self.stock, const.TIMEFRAME[timeframe][0] , utc_from, size, mt5.COPY_TICKS_ALL) 
        data = self.convert2Array(d)
        return data

# -----
    
def test(size):
    server = PyMT5('USDJPY')
    ohlcv, dic =  server.download('M1', size=size) 
    print(ohlcv)
    print(dic[const.TIMEJST])

if __name__ == "__main__":
    test(3)