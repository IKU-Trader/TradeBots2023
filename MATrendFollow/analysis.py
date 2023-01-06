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

from time_utility import pyTime, TIMEZONE_TOKYO
from CandleChart import CandleChart, gridFig
from STA import analysis, arrays2dic, SMA, WINDOW
from const import TIME

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
    t1 = pyTime(2019, 8, 9, 5, 0, 0, TIMEZONE_TOKYO)
    tohlcv = server.getTohlcv(time_from=t0, time_to=t1)
    fig, axes = gridFig([8, 2], (15, 5))
    chart = CandleChart(fig, axes[0], 'dji')
    dic = arrays2dic(tohlcv)
    analysis(dic, SMA, {WINDOW: 5}, name='SMA5')
    analysis(dic, SMA, {WINDOW: 20}, name='SMA20')
    analysis(dic, SMA, {WINDOW: 60}, name='SMA60')
    chart.drawCandle(dic)
    chart.drawLine(dic[TIME], dic['SMA5'])
    chart.drawLine(dic[TIME], dic['SMA20'], color='green')
    chart.drawLine(dic[TIME], dic['SMA60'], color='blue')
    
    


if __name__ == '__main__':
    test2()