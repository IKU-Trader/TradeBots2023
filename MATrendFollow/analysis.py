# -*- coding: utf-8 -*-
"""
Created on Tue Jan  3 16:25:10 2023

@author: IKU-Trader
"""
import pandas as pd
import sys
sys.path.append("../libs")
sys.path.append("../libs/PyCandleChart")
sys.path.append("../libs/TA")

from DataServerStub import DataServerStub
from DataBuffer import DataBuffer

from datetime import timedelta
from time_util import pyTime, TIMEZONE_TOKYO
from CandleChart import CandleChart, BandPlot, gridFig, Colors
from STA import seqIndicator, indicator, arrays2dic, SMA, WINDOW, MA_TREND_BAND, THRESHOLD, MA_KEYS, PATTERNS, SOURCE, PATTERN_MATCH
from STA import UPPER_TREND, UPPER_SUB_TREND, UPPER_DIP, LOWER_TREND, LOWER_SUB_TREND, LOWER_DIP, NO_TREND
from const import TIME, OPEN, HIGH, LOW, CLOSE, VOLUME, UNIT_MINUTE
from util import sliceTohlcv


def day_trade(tohlcv:dict, year:int, month:int, day:int):
    #t0 = pyTime(year, month, day, 0, 0, 0, TIMEZONE_TOKYO)
    t1 = pyTime(year, month, day, 20, 0, 0, TIMEZONE_TOKYO)
    t2 = t1 + timedelta(hours=8)
    dic = sliceTohlcv(tohlcv, t1, t2)
    fig, axes = gridFig([8, 1], (15, 5))
    chart1 = CandleChart(fig, axes[0], 'dji')
    chart1.drawCandle(dic)
    chart1.drawLine(dic[TIME], dic['SMA5'], label='SMA5')
    chart1.drawLine(dic[TIME], dic['SMA20'], color='green', label='SMA20')
    chart1.drawLine(dic[TIME], dic['SMA60'], color='blue', label='SMA60')
    chart1.drawMarkers(dic[TIME], dic[LOW], -50, dic['SIGNAL'], 1, '^', 'green', overlay=1, markersize=20)
    chart1.drawMarkers(dic[TIME], dic[LOW], -50, dic['SIGNAL'], 2, '^', 'green', overlay=2, markersize=20)
    chart1.drawMarkers(dic[TIME], dic[HIGH], 
                       50, dic['SIGNAL'], -1, '^', 'red', overlay=1, markersize=20)
    chart1.drawMarkers(dic[TIME], dic[HIGH], 50, dic['SIGNAL'], -2, '^', 'red', overlay=2, markersize=20)
    
    chart2 = BandPlot(fig, axes[1], 'MA Trend')
    colors = {UPPER_TREND: 'red',
              UPPER_SUB_TREND: Colors.light_red,
              UPPER_DIP: 'black',
              LOWER_TREND: 'green',
              LOWER_SUB_TREND: Colors.light_green,
              LOWER_DIP: 'black',
              NO_TREND: 'gray'}
    chart2.drawBand(dic[TIME], dic['MA_TREND'], colors=colors)

def trades():
    server = DataServerStub('DJI')
    server.importFile('../data/DJI_Feature_2019.csv')
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
    buffer = DataBuffer(server.tohlcv, params, 5)
    day_trade(buffer.dic, 2019, 8, 8)
    
if __name__ == '__main__':
    trades()