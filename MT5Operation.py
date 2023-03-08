# -*- coding: utf-8 -*-
"""
Created on Tue Mar  7 13:39:13 2023

@author: IKU-Trader
"""

import sys
sys.path.append('./libs')
sys.path.append('./libs/PyCandleChart')
sys.path.append('./libs/PyMT5')
sys.path.append('./libs/TA')

import pandas as pd
import ipywidgets as widgets

import plotly.graph_objects as go
from datetime import datetime

from const import const
from mt5_const import mt5_const
from TimeUtils import TimeUtils
from Utils import Utils

from PyMT5 import PyMT5
from STA import TechnicalAnalysis as ta
from CandleChart import CandleChart, BandPlot, makeFig, gridFig, Colors
from DataBuffer import DataBuffer

TICKERS = ['DOWUSD', 'S&PUSD', 'JPXJPY', 'XAUUSD', 'XAGUSD', 'WTIUSD', 'USDJPY', 'GBPJPY', 'AUDUSD']
TIMEFRAMES = ['M1', 'M5', 'M15', 'M30', 'H1', 'H4', 'H8', 'D1']



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

class MT5Operation:    
    def __init__(self, display):
        self.display = display
        mt5 = PyMT5(TimeUtils.TIMEZONE_TOKYO)
        self.mt5 = mt5
        self.initGui()
        self.fig = None
        self.ax = None
    
    def createButton(self, text: str, receiver):
        button = widgets.Button(description=text)
        button.on_click(receiver)
        return button
    
    def createComboBox(self, options: list, receiver):
        select = widgets.Select(options=options)
        select.observe(receiver)
        return select

    def createTextBox(self):
        box = widgets.Output(layout={'border': '1px solid black'})
        return box
    
    def createIntBox(self, value, min, max, step):
        box = widgets.BoundedIntText(value=value, min=min, max=max, step=step)
        return box
    
    def initGui(self):
        ticker = self.createComboBox(TICKERS, self.tickerChanged)
        timeframe = self.createComboBox(TIMEFRAMES, self.timeframeChanged)
        data_size = self.createIntBox(200, 100, 10000, 100)
        download = self.createButton('Download', self.downloadClicked)
        draw = self.createButton('Draw chart', self.drawClicked)
        hbox = widgets.HBox([ticker, timeframe, data_size, download, draw])
        self.ticker = ticker
        self.timeframe = timeframe
        self.data_size = data_size
        self.display(hbox)
        
    def tickerChanged(self, value):
        self.ticker_value = value
        
    def timeframeChanged(self, value):
        self.interval_value = value

    def downloadClicked(self, value):        
        symbol = self.ticker.value
        timeframe = self.timeframe.value
        size = int(self.data_size.value)
        #self.display([symbol, timeframe, size])
        dic = self.mt5.download(symbol, timeframe, size)
        ta_param = createIndicator()
        buffer = DataBuffer([dic[const.TIME], dic[const.OPEN], dic[const.HIGH], dic[const.LOW], dic[const.CLOSE], dic[const.VOLUME]], ta_param)        
        #self.dic = Utils.sliceDicLast(buffer.dic, size)    
        self.dic = buffer.dic
        #print(self.dic[const.TIME][-10:])            
        #dic = Utils.sliceTohlcvWithLength(tohlcv, t, 24 * 60 / 5)

    def drawClicked(self, value):
        self.drawCandleChart2(self.dic, self.ticker.value)
        
    def drawCandleChart(self, dic: dict, symbol: str):
        def dateStr(t):
            s = f'{t.year}/{t.month}/{t.day}'
            return s
        
        print('LastTime ', dic[const.TIME][-1])
        fig, ax = makeFig(1, 1, (20, 10))
        t0 = dic[const.TIME][0]
        t1 = dic[const.TIME][-1]
        title = symbol + ' ' + dateStr(t0) + '-' + dateStr(t1)
        chart1 = CandleChart(fig, ax, title, date_format=CandleChart.DATE_FORMAT_DAY_HOUR)
        chart1.drawCandle(dic)
        chart1.drawLine(dic[const.TIME], dic['SMA5'], label='SMA5')
        chart1.drawLine(dic[const.TIME], dic['SMA20'], color='green', label='SMA20')
        chart1.drawLine(dic[const.TIME], dic['SMA60'], color='blue', label='SMA60')
        chart1.drawMarkers(dic[const.TIME], dic[const.LOW], -50, dic['SIGNAL'], 1, '^', 'green', overlay=1, markersize=16)
        chart1.drawMarkers(dic[const.TIME], dic[const.LOW], -50, dic['SIGNAL'], 2, '^', 'green', overlay=2, markersize=16)
        chart1.drawMarkers(dic[const.TIME], dic[const.HIGH], 50, dic['SIGNAL'], -1, 'v', 'red', overlay=1, markersize=16)
        chart1.drawMarkers(dic[const.TIME], dic[const.HIGH], 50, dic['SIGNAL'], -2, 'v', 'red', overlay=2, markersize=16) 
    
    def drawCandleChart2(self, dic: dict, symbol: str):
        fig = go.Figure(data=[go.Candlestick(x=dic[const.TIME], open=dic[const.OPEN], high=dic[const.HIGH], low=dic[const.LOW], close=dic[const.CLOSE])])
        fig.show()
# -----
    
    
def test():
    server = PyMT5(TimeUtils.TIMEZONE_TOKYO)
    dic = server.download('DOWUSD', 'M5', 200)
    print(dic)
    
if __name__ == '__main__':
    test()  

