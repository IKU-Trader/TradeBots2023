# -*- coding: utf-8 -*-
"""
Created on Tue Jan  3 16:25:10 2023

@author: IKU-Trader
"""

import sys
sys.path.append("../libs")
sys.path.append("../libs/PyCandleChart")
sys.path.append("../libs/TA")

from DataServerStub import DataServerStub
from DataBuffer import DataBuffer

from TimeUtils import TimeUtils
from CandleChart import CandleChart, BandPlot, gridFig, Colors
from TA.STA import TechnicalAnalysis as ta
from libs.const import const
from libs.Utils import Utils

def dateStr(t):
    s = f'{t.year}/{t.month}/{t.day}'
    return s
    
def day_trade(tohlcv:dict, year:int, month:int, day:int):
    #t0 = pyTime(year, month, day, 0, 0, 0, TIMEZONE_TOKYO)
    t = TimeUtils.pyTime(year, month, day, 20, 0, 0, TimeUtils.TIMEZONE_TOKYO)
    dic = Utils.sliceTohlcvWithLength(tohlcv, t, 24 * 60 / 5)
    fig, axes = gridFig([8, 1], (30, 5))
    t0 = dic[const.TIME][0]
    t1 = dic[const.TIME][-1]
    title = 'dji ' + dateStr(t0) + '-' + dateStr(t1)
    chart1 = CandleChart(fig, axes[0], title, date_format=CandleChart.DATE_FORMAT_DAY_HOUR)
    chart1.drawCandle(dic)
    chart1.drawLine(dic[const.TIME], dic['SMA5'], label='SMA5')
    chart1.drawLine(dic[const.TIME], dic['SMA20'], color='green', label='SMA20')
    chart1.drawLine(dic[const.TIME], dic['SMA60'], color='blue', label='SMA60')
    chart1.drawMarkers(dic[const.TIME], dic[const.LOW], -50, dic['SIGNAL'], 1, '^', 'green', overlay=1, markersize=20)
    chart1.drawMarkers(dic[const.TIME], dic[const.LOW], -50, dic['SIGNAL'], 2, '^', 'green', overlay=2, markersize=20)
    chart1.drawMarkers(dic[const.TIME], dic[const.HIGH], 
                       50, dic['SIGNAL'], -1, '^', 'red', overlay=1, markersize=20)
    chart1.drawMarkers(dic[const.TIME], dic[const.HIGH], 50, dic['SIGNAL'], -2, '^', 'red', overlay=2, markersize=20)
    chart2 = BandPlot(fig, axes[1], 'MA Trend', date_format=CandleChart.DATE_FORMAT_DAY_HOUR)
    colors = {ta.UPPER_TREND: 'red',
              ta.UPPER_SUB_TREND: Colors.light_red,
              ta.UPPER_DIP: 'black',
              ta.LOWER_TREND: 'green',
              ta.LOWER_SUB_TREND: Colors.light_green,
              ta.LOWER_DIP: 'black',
              ta.NO_TREND: 'gray'}
    chart2.drawBand(dic[const.TIME], dic['MA_TREND'], colors=colors)

def trades():
    server = DataServerStub('DJI')
    server.importFile('../data/DJI/DJI_Feature_2019.csv')
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
    buffer = DataBuffer(server.tohlcv, params, 5)
    day_trade(buffer.dic, 2019, 8, 7)
    
if __name__ == '__main__':
    trades()