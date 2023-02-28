# -*- coding: utf-8 -*-
"""
Created on Tue Feb 28 14:42:24 2023

@author: docs9
"""
import os
import pandas as pd
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



def test():
    server = DataServerStub('DJI')
    server.importFile('../data/DJI_Feature_2019_08.csv')
    tohlcv_list = server.init(100, step_sec=10)
    
    ta = createIndicator()
    buffer = DataBuffer(tohlcv_list, ta, 5)


    
    print(tohlcv_list)

    for i in range(20):
        tohlcv = server.nextData()
        print(tohlcv)
        buffer.update(tohlcv)
    
    
if __name__ == '__main__':
    test()    