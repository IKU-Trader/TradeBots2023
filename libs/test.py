# -*- coding: utf-8 -*-
"""
Created on Tue Feb 28 14:42:24 2023

@author: IKU-Trader
"""
import os
import pandas as pd
import numpy as np
import glob
import pytz
from TimeUtils import TimeUtils
from Utils import Utils
from datetime import datetime, timedelta
import random

from DataServerStub import DataServerStub
from DataBuffer import DataBuffer

from TA.STA import TechnicalAnalysis as ta


def createIndicator():
    params = {}
    params['SMA5'] = [ta.SMA, {ta.WINDOW: 5}]
    params['SMA20'] = [ta.SMA, {ta.WINDOW: 20}]
    params['SMA60'] = [ta.SMA, {ta.WINDOW: 60}]
    params['MA_TREND'] = [ta.MA_TREND_BAND, {ta.MA_KEYS:['SMA5', 'SMA20', 'SMA60'], ta.THRESHOLD:0.05}]
    patterns = {    ta.SOURCE: 'MA_TREND',
                    ta.PATTERNS:[
                            [[ta.NO_TREND, ta.UPPER_TREND], 1, 0],
                            [[ta.UPPER_SUB_TREND, ta.UPPER_TREND], 1, 0],
                            [[ta.UPPER_DIP, ta.UPPER_TREND], 2, 0],
                            [[ta.NO_TREND, ta.LOWER_TREND], -1, 0],
                            [[ta.LOWER_SUB_TREND, ta.LOWER_TREND], -1, 0],
                            [[ta.LOWER_DIP, ta.LOWER_TREND], -2, 0]
                            ]}
    params['SIGNAL'] = [ta.PATTERN_MATCH, patterns]
    return params

def saveCandles(filepath, candles:list):
    f = open(filepath, mode='w')
    for candle in candles:
        s = ''
        for value in candle:
            if isNan(value):
                s += ','
            else:
                s += str(value) + ','
        s = s[:-1]
        f.write(s + '\n')
    f.close()
    
    
def isNan(value):
    if type(value) == float or type(value) == int:
        return np.isnan(value)    
    return False
    
def saveDic(filepath, dic):
    f = open(filepath, mode='w')
    arrays = []
    for key, value in dic.items():
        arrays.append(value)
    header = ''
    for key in dic.keys():
        header += key + ','
    header = header[:-1]
    f.write(header + '\n')
    for i in range(len(arrays[0])):
        s = ''
        for array in arrays:
            if isNan(array[i]):
                s += ','
            else:
                s += str(array[i]) + ','
        s = s[:-1]
        f.write(s + '\n')
    f.close()    
    
def test():
    server = DataServerStub('DJI')
    server.importFile('../data/DJI/DJI_Feature_2019_08.csv')
    tohlcv_list = server.init(100, step_sec=10)
    
    ta = createIndicator()
    buffer = DataBuffer(tohlcv_list, ta, 5)
    
    print(tohlcv_list)
    Utils.makeDir('../debug/')
    for i in range(100):
        tohlcv = server.nextData()
        print(tohlcv)
        if i == 10:
            print(i)
            pass
        buffer.update(tohlcv)
        d1 = buffer.tohlcvDic()
        saveDic(f'../debug/d1_{i}.csv', d1)
        t2, d2 = buffer.temporary()
        saveDic(f'../debug/d2_{i}.csv', d2)
        
    
if __name__ == '__main__':
    test()    