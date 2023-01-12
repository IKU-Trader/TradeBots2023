
import pandas as pd
import sys
sys.path.append("../libs")
sys.path.append("../libs/PyCandleChart")
sys.path.append("../libs/TA")

from const import UNIT_MINUTE
from DataServerStub import DataServerStub
from DataBuffer import DataBuffer

from time_util import pyTime, TIMEZONE_TOKYO
from CandleChart import CandleChart, BandPlot, gridFig
from STA import indicator, arrays2dic, SMA, WINDOW, MA_TREND_BAND, THRESHOLD, MA_KEYS, PATTERNS, SOURCE, PATTERN_MATCH
from STA import UPPER_TREND, UPPER_SUB_TREND, LOWER_TREND, LOWER_SUB_TREND, NO_TREND
from const import TIME, OPEN, HIGH, LOW, CLOSE, VOLUME
from util import sliceTohlcv

def TAParams():
    trend_params = {MA_KEYS:['SMA5', 'SMA20', 'SMA60'], THRESHOLD:0.05}
    patterns = {
                    SOURCE: 'MA_TREND',
                    PATTERNS:[
                            [[NO_TREND, UPPER_TREND], 1, 0],
                            [[UPPER_SUB_TREND, UPPER_TREND], 1, 0],
                            [[NO_TREND, LOWER_TREND], 2, 0],
                            [[LOWER_SUB_TREND, LOWER_TREND], 2, 0]
                            ]
                }

    params = [
                [SMA, {WINDOW: 5}, 'SMA5'],
                [SMA, {WINDOW: 20}, 'SMA20'],
                [SMA, {WINDOW: 60}, 'SMA60'],
                [MA_TREND_BAND, trend_params, 'MA_TREND'],
                [PATTERN_MATCH, patterns, 'SIGNAL']
            ]
    return params

def init():
    server = DataServerStub('DJI')
    server.importFile('../data/DJI_Feature_2019_08.csv')
    n = server.size()
    tohlcv = server.init(100)
    buffer = DataBuffer(tohlcv, TAParams(), 5)
    for i in range(n):
        tohlcv = server.next()
        if tohlcv is None:
            break
        candles = buffer.toCandles(tohlcv)
        buffer.update(candles)
        
    pass

def daytrade():
    init()
    pass


if __name__ == '__main__':
    daytrade()