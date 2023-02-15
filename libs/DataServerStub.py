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
        
    def init(self, initial_num:int, step_num=10):
        self.index = initial_num
        self.step_num = step_num
        self.step = 0
        tohlcv = self.sliceData(0, initial_num - 1)
        return tohlcv


    def interpolate(self, index, step):
        tohlcv1 = self.sliceData(index, index)
        tohlcv2 = self.sliceData(index + 1, index + 1)
        dt = tohlcv2[0] - tohlcv1[0]
        if dt != timedelta(minutes=1):
            return []
        
        if step == self.stem_num - 1:
            return (tohlcv2, index + 1, 0)

        price = []
        h = tohlcv2[2]
        l = tohlcv2[3]
        c = tohlcv2[4]
        for i in range(self.step_num - 2):
            p = l + (h - l) * i / (self.step_num - 2)
            price.append(p)
        price.append(c)
        random.shuffle(c)
            
            
        t = tohlcv1[0] + timedelta(minutes=int(60/step))
        o = tohlcv2[1]
        
        
        

    def nextData(self):
        if self.index > self.size() - 1:
            return None
        
        if self.step == self.step_num - 1:
            self.index += 1
            self.step = 0
            self.dummy_tohlcv = self.interpolate(self.index)
            self.step = 1
            return 


        self.step += 1
        
        return self.dummy_tohlcv[self.step]

    def sliceData(self, begin: int, end: int):
        out = []
        for array in self.tohlcv:
            out.append(array[begin: end + 1])
        return out

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