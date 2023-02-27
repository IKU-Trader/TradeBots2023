# -*- coding: utf-8 -*-
"""
Created on Tue Jan  3 16:26:45 2023

@author: IKU-Trader
"""
import os
import pandas as pd
import glob
import pytz
from time_util import changeTimezone, TIMEZONE_TOKYO, str2pytimeArray, pyTime
from util import sliceTime
from datetime import datetime, timedelta
import random

import numpy as np


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
    def __init__(self, name:str):
        self.name = name
        pass
  
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
        self.tohlcv = tohlcv
        
    def init(self, initial_num:int, step_sec=0):
        self.currentIndex = initial_num - 1
        tohlcv = self.sliceTohlcv(0, self.currentIndex)
        if step_sec == 0:
            self.step_num = 0
        else:
            self.step_num = int(60 / step_sec) - 1
            self.dummy = self.makeDummy(self.tohlcvAt(self.currentIndex + 1), self.step_sec, self.step_num)
        self.step = 0
        return tohlcv


    def makeDummy(self, next_tohlcv, tstep, num):
        t = next_tohlcv[0]
        lo = next_tohlcv[3]
        hi = next_tohlcv[2]
        buffer = np.arange(lo, hi + 1, (hi - lo) / (num - 1))
        np.random.shuffle(buffer)
        dummy = []
        o = next_tohlcv[1]
        h = o
        l = o
        for i, price in enumerate(buffer):
            if i > 0:
                if price > h:
                    h = price
                if price < l:
                    l = price
            dummy.append([t, o, h, l, price]) 
        return dummy
        

    def nextData(self):        
        if self.step_num == 0:
            self.currentIndex += 1
            if self.currentIndex > self.size() - 1:
                return None
            else:
                return self.tohlcAt(self.currentIndex)
        else:
            tohlcv = self.dummy
            self.index += 1
            self.step = 0
            self.dummy_tohlcv = self.interpolate(self.index)
            self.step = 1
            return 


        self.step += 1
        
        return self.dummy[self.step]

    def sliceTohlcv(self, begin: int, end: int):
        out = []
        for array in self.tohlcv:
            out.append(array[begin: end + 1])
        return out
    
    def tohlcvAt(self, index):
        return self.tohlcv[index]

    def timeRange(self):
        t0 = self.tohlcv[0][0]
        t1 = self.tohlcv[0][-1]
        return (t0, t1)

    def size(self):
        return len(self.tohlcv[0])
    
    def getCandles(self, time_from=None, time_to=None):
        tohlcv = self.getTohlcv(time_from=time_from, time_to=time_to)
        if len(tohlcv) == 0:
            return []
        return self.toCandles(tohlcv)

    def toTohlcv(self, candles:[]):
        n = len(candles)
        m = len(candles[0])
        arrays = []
        for i in range(m):
            array = [candles[j][i] for j in range(n)]
            arrays.append(array)
        return arrays
# -----
        
def test():
    server = DataServerStub('DJI')
    server.importFile('../data/DJI_Feature_2019_08.csv')
    tohlcv = server.init(100)
    tohlcv = server.next()
    pass


def test1():
    server = DataServerStub('DJI')
    server.importFile('../data/DJI_Feature_2019_08.csv')
    t0 = pyTime(2019, 8, 9, 0, 0, 0, TIMEZONE_TOKYO)
    t1 = pyTime(2019, 8, 10, 0, 0, 0, TIMEZONE_TOKYO)
    candles = server.getCandles()
    df = pd.DataFrame(data=candles, columns=['Time', 'Open', 'High', 'Low', 'Close', 'Volume'])
    df.to_csv('validation.csv', index=False)

if __name__ == '__main__':
    test()