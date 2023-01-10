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

from DataServerStub import UNIT_MINUTE
from DataServerStub import DataServerStub

from time_util import pyTime, TIMEZONE_TOKYO
from CandleChart import CandleChart, BandPlot, gridFig
from STA import analysis, arrays2dic, SMA, WINDOW, MA_TREND_BAND, THRESHOLD, MA_KEYS, PATTERNS, SOURCE, PATTERN_MATCH
from STA import UPPER_TREND, UPPER_SUB_TREND, LOWER_TREND, LOWER_SUB_TREND, NO_TREND
from const import TIME, OPEN, HIGH, LOW, CLOSE, VOLUME
from util import sliceTohlcv

def test1():
    server = DataServerStub('DJI', 5, UNIT_MINUTE)
    server.importFile('../data/DJI_Feature_2019_08.csv')
    t0 = pyTime(2019, 8, 9, 0, 0, 0, TIMEZONE_TOKYO)
    t1 = pyTime(2019, 8, 10, 0, 0, 0, TIMEZONE_TOKYO)
    candles = server.getCandles()
    df = pd.DataFrame(data=candles, columns=['Time', 'Open', 'High', 'Low', 'Close', 'Volume'])
    df.to_csv('validation.csv', index=False)

def test2():
    server = DataServerStub('DJI', 5, UNIT_MINUTE)
    server.importFile('../data/DJI_Feature_2019_08.csv')
    t0 = pyTime(2019, 8, 8, 0, 0, 0, TIMEZONE_TOKYO)
    t1 = pyTime(2019, 8, 8, 9, 0, 0, TIMEZONE_TOKYO)
    t2 = pyTime(2019, 8, 9, 6, 0, 0, TIMEZONE_TOKYO)
    tohlcv = server.getTohlcv(time_from=t0, time_to=t2)
    fig, axes = gridFig([8, 1], (15, 5))
    chart1 = CandleChart(fig, axes[0], 'dji')
    dic = arrays2dic(tohlcv)
    analysis(dic, SMA, {WINDOW: 5}, name='SMA5')
    analysis(dic, SMA, {WINDOW: 20}, name='SMA20')
    analysis(dic, SMA, {WINDOW: 60}, name='SMA60')
    params = {MA_KEYS:['SMA5', 'SMA20', 'SMA60'], THRESHOLD:0.05}
    analysis(dic, MA_TREND_BAND, params, name='MA_TREND')
    patterns = {    SOURCE: 'MA_TREND',
                    PATTERNS:[
                            [[NO_TREND, UPPER_TREND], 1, 0],
                            [[UPPER_SUB_TREND, UPPER_TREND], 1, 0],
                            [[NO_TREND, LOWER_TREND], 2, 0],
                            [[LOWER_SUB_TREND, LOWER_TREND], 2, 0]
                            ]}
    analysis(dic, PATTERN_MATCH, patterns, 'SIGNAL')
    
    dic2 = sliceTohlcv(dic, t1, t2)
    chart1.drawCandle(dic2)
    chart1.drawLine(dic2[TIME], dic2['SMA5'], label='SMA5')
    chart1.drawLine(dic2[TIME], dic2['SMA20'], color='green', label='SMA20')
    chart1.drawLine(dic2[TIME], dic2['SMA60'], color='blue', label='SMA60')
    chart1.drawMarkers(dic2[TIME], dic2[LOW], -50, dic2['SIGNAL'], 1, '^', 'green', overlay=1, markersize=20)
    chart1.drawMarkers(dic2[TIME], dic2[HIGH], 50, dic2['SIGNAL'], 2, 'v', 'red', overlay=2, markersize=20)
    
    chart2 = BandPlot(fig, axes[1], 'MA Trend')
    colors = {0:'white',
              UPPER_TREND:'red',
              UPPER_SUB_TREND:'orange',
              LOWER_TREND:'green',
              LOWER_SUB_TREND: 'yellow',
              NO_TREND: 'gray'}
    chart2.drawBand(dic2[TIME], dic2['MA_TREND'], colors=colors)


if __name__ == '__main__':
    test2()