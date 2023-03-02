# -*- coding: utf-8 -*-
"""
Created on Tue Feb 28 14:42:24 2023

@author: docs9
"""
import os
import pandas as pd
import numpy as np
import glob
import pytz
from time_util import changeTimezone, TIMEZONE_TOKYO, str2pytimeArray, pyTime
from util import sliceTime
from datetime import datetime, timedelta
import random

from DataServerStub import DataServerStub
from DataBuffer import DataBuffer

from STA import seqIndicator, indicator, arrays2dic, SMA, WINDOW, MA_TREND_BAND, THRESHOLD, MA_KEYS, PATTERNS, SOURCE, PATTERN_MATCH
from STA import UPPER_TREND, UPPER_SUB_TREND, UPPER_DIP, LOWER_TREND, LOWER_SUB_TREND, LOWER_DIP, NO_TREND


def createIndicator():
    params = {}
    params['SMA5'] = [SMA, {WINDOW: 5}]
    params['SMA20'] = [SMA, {WINDOW: 20}]
    params['SMA60'] = [SMA, {WINDOW: 60}]
    params['MA_TREND'] = [MA_TREND_BAND, {MA_KEYS:['SMA5', 'SMA20', 'SMA60'], THRESHOLD:0.05}]
    patterns = {    SOURCE: 'MA_TREND',
                    PATTERNS:[
                            [[NO_TREND, UPPER_TREND], 1, 0],
                            [[UPPER_SUB_TREND, UPPER_TREND], 1, 0],
                            [[UPPER_DIP, UPPER_TREND], 2, 0],
                            [[NO_TREND, LOWER_TREND], -1, 0],
                            [[LOWER_SUB_TREND, LOWER_TREND], -1, 0],
                            [[LOWER_DIP, LOWER_TREND], -2, 0]
                            ]}
    params['SIGNAL'] = [PATTERN_MATCH, patterns]
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
    server.importFile('../data/DJI_Feature_2019_08.csv')
    tohlcv_list = server.init(100, step_sec=20)
    
    ta = createIndicator()
    buffer = DataBuffer(tohlcv_list, ta, 5)
    
    print(tohlcv_list)
    #os.mkdir('../debug/')
    for i in range(20):
        tohlcv = server.nextData()
        print(tohlcv)
        buffer.update(tohlcv)
        d1 = buffer.tohlcvDic()
        saveDic(f'../debug/d1_{i}.csv', d1)
        t2, d2 = buffer.temporary()
        saveDic(f'../debug/d2_{i}.csv', d2)
        
    
if __name__ == '__main__':
    test()    