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

from const import const
from TimeUtils import TimeUtils
from Utils import Utils

from PyMT5 import PyMT5
from STA import TechnicalAnalysis as ta
from CandleChart import CandleChart, BandPlot, gridFig, Colors
from DataBuffer import DataBuffer

TICKERS = ['DOWUSD', 'S&PUSD', 'JPXJPY', 'XAUUSD', 'XAGUSD', 'WTIUSD', 'USDJPY', 'GBPJPY', 'AUDUSD']
TIMEFRAMES = ['M1', 'M5', 'M15', 'M30', 'H1', 'H4', 'H8', 'D1']

class MT5Operation:    
    def __init__(self, display):
        self.display = display
        mt5 = PyMT5()
        self.mt5 = mt5
        self.initGui()
    
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
        data_size = self.createIntBox(500, 100, 10000, 100)
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
        self.display([symbol, timeframe, size])
        (ohlcv, dic) = self.mt5.download(symbol, timeframe, size)                
        self.dic = dic
        
    def drawClicked(self, value):
                
        pass
    

    
# -----
    
    
def test():
    server = PyMT5()
    pos = server.positions('USDJPY')
    print(pos)
    
if __name__ == '__main__':
    test()  

