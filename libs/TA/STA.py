# -*- coding: utf-8 -*-
"""
Created on Wed Jan  4 18:19:54 2023

@author: IKU-Trader
"""

import sys
sys.path.append("../")

import numpy as np
from Utils import Utils
from MathArray import MathArray

TIME = 'time'
OPEN = 'open'
HIGH = 'high'
LOW = 'low'
CLOSE = 'close'
VOLUME = 'volume'

TAMethod = str
ATR: TAMethod = 'atr'
TR: TAMethod = 'tr'
SMA: TAMethod = 'sma'
HL2: TAMethod = 'hl2'
ATR_BAND_UPPER: TAMethod = 'atr_band_upper'
ATR_BAND_LOWER: TAMethod = 'atr_band_lower'
ATR_BREAKUP_SIGNAL: TAMethod = 'atr_breakup_signal'
ATR_BREAKDOWN_SIGNAL: TAMethod = 'atr_breakdown_signal'

MA_TREND_BAND: TAMethod = 'ma_trend_band'
PATTERN_MATCH: TAMethod = 'pattern_match'


TAParam = str
WINDOW: TAParam = 'window'
COEFF: TAParam = 'coeff'

# MA Trend
THRESHOLD: TAParam = 'threshold'
MA_KEYS: TAParam  = 'ma_keys'
NO_TREND = 0
UPPER_TREND = 1
UPPER_SUB_TREND = 2
UPPER_DIP =  3
LOWER_TREND = -1
LOWER_SUB_TREND = -2
LOWER_DIP = -3

SOURCE: TAParam = 'source'
PATTERNS: TAParam = 'patterns'


def nans(length):
    out = []
    for i in range(length):
        out.append(np.nan)
    return out

def arrays2dic(tohlcv:[]):
    dic = {}
    dic[TIME] = tohlcv[0]
    dic[OPEN] = tohlcv[1]
    dic[HIGH] = tohlcv[2]
    dic[LOW] = tohlcv[3]
    dic[CLOSE] = tohlcv[4]
    if len(tohlcv) > 5:
        dic[VOLUME] = tohlcv[5]
    return dic

class TechnicalAnalysis:
    
    @classmethod 
    def candleBody(cls, open_price, high_price, low_price, close_price):
        body_low = min([high_price, low_price])
        body_high = max([high_price, low_price])
        body = body_high - body_low
        is_positive = close_price > open_price
        spike_high = high_price - body_high
        spike_low = body_low - low_price
        return (is_positive, body, body_low, body_high)
    
    @classmethod 
    def candleSpike(cls, open_price, high_price, low_price, close_price):
        is_positive, body, body_low, body_high = cls.candleBodey(open_price, high_price, low_price, close_price)
        spike_high = high_price - body_high
        spike_low = body_low - low_price
        return (spike_high, spike_low)

    @classmethod 
    def hl2(cls, dic):
        high = dic[HIGH]
        low = dic[LOW]
        out = MathArray.addArray(high, low)
        out = MathArray.multiply(out, 0.5)
        return out
    
    @classmethod
    def sma(cls, array, window):
        n = len(array)
        out = nans(n)
        for i in range(window - 1, n):
            s = 0.0
            count = 0
            for j in range(window):
                a = array[i - j]
                if np.isnan(a):
                    continue
                else:
                    count += 1
                    s += a
            if count > 0:                
                out[i] = s / count
        return out            

    @classmethod            
    def tr(cls, dic):
        high = dic[HIGH]
        low = dic[LOW]
        close = dic[CLOSE]
        
        n = len(close)
        out = nans(n)
        out[0] = high[0] - low[0]
        for i in range(1, n):
            r1 = np.abs(high[i] - low[i])
            r2 = np.abs(high[i] - close[i - 1])
            r3 = np.abs(close[i - 1] - low[i])
            out[i] = np.max([r1, r2, r3])
        return out
       
    @classmethod
    def atr(cls, dic, window):
        trdata = cls.tr(dic)
        out = cls.sma(trdata, window)
        return (out, trdata)
    
    @classmethod
    def atrBand(cls, dic, k):
        atr = dic[ATR]
        inp = dic[CLOSE]
        m =  MathArray.multiply(atr, k)
        upper = MathArray.addArray(inp, m)
        lower = MathArray.subtractArray(inp, m)
        return (upper, lower)
    
    @classmethod
    def breakSignal(cls, dic, key, is_up, offset=1):
        if offset < 0:
            return None
        level = dic[key]
        oo = dic[OPEN]
        hh = dic[HIGH]
        ll = dic[LOW]
        cc = dic[CLOSE]
        n = len(cc)
        signal = []
        for i in range(n):
            if i < offset:
                signal.append(0)
                continue
            if is_up:
                p = max(oo[i], cc[i])
                t = p > level[i - offset]
            else:
                p = min(oo[i], cc[i])
                t = p < level[i - offset]
            if t:
                signal.append(1)
            else:
                signal.append(0)
        return signal
    
    @classmethod
    def maTrendBand(cls, op, hi, lo, cl, ma_list, threshold):
        w1 = MathArray.subtractArray(ma_list[0], ma_list[1])
        w2 = MathArray.subtractArray(ma_list[1], ma_list[2])
        n = len(w1)
        out = MathArray.full(n, NO_TREND)
        for i in range(n):
            if w1[i] > 0 and w2[i] > 0:
                out[i] = UPPER_TREND
            elif w1[i] > 0 and w2[i] < 0:
                out[i] = UPPER_SUB_TREND
            elif w1[i] < 0 and w2[i] < 0:
                out[i] = LOWER_TREND
            elif w1[i] < 0 and w2[i] > 0:
                out[i] = LOWER_SUB_TREND
            if out[i] == UPPER_TREND:
                (is_positive, body, body_low, body_high) = cls.candleBody(op[i], hi[i], lo[i], cl[i])
                if ma_list[1][i] > body_low:
                    out[i] = UPPER_DIP
            if out[i] == LOWER_TREND:
                (is_positive, body, body_low, body_high) = cls.candleBody(op[i], hi[i], lo[i], cl[i])
                if ma_list[1][i] < body_high:
                    out[i] = LOWER_DIP            
            if abs(w1[i] / ma_list[1][i] * 100.0) < threshold and abs(w2[i] / ma_list[2][i] * 100.0 < threshold):
                out[i] = NO_TREND
        return out
    
    @classmethod 
    def patternMatching(cls, signal, patterns):
        n = len(signal)
        out = MathArray.full(n, np.nan)
        for [pattern, value, offset] in patterns:
            m = len(pattern)
            for i in range(n - m):
                if signal[i: i + m] == pattern:
                    out[i + m  - 1 + offset] = value
        return out
    
# -----
def seqIndicator(dic: dict, key: str, begin: int, end:int, params: dict, name:str=None):
    if name is None:
        name = key
    n = len(dic[OPEN])
    if WINDOW in params.keys():
        window = params[WINDOW]
    else:
        window = 0
    if not name in dic.keys():
        data = dic
        begin = 0
        end = n - 1
    else:
        if window > 0:
            if begin < window:
                data = dic
            else:
                data = Utils.sliceDic(dic, begin - window, end)
        else:
            data = Utils.sliceDic(dic, begin, end)
    array = indicator(data, key, params, name=name, should_set=False)    
    if array is None:
        return False
    original = dic[name]
    if name in dic.keys():
        j = len(array) - (end - begin + 1)
        original[begin: end + 1] = array[j:]
    else:
        original[name] = array
    return True

def indicator(data:dict, key:str, params:dict, name:str=None, should_set=True):
    if WINDOW in params.keys():
        window = params[WINDOW]
    if COEFF in params.keys():
        coeff = params[COEFF]        
    if key == SMA:
        array = TechnicalAnalysis.sma(data[CLOSE], window)
    elif key == ATR:
        array, _ = TechnicalAnalysis.atr(data, window)
    elif key == ATR_BAND_UPPER or key == ATR_BAND_LOWER:
        coeff = params[COEFF]
        upper, lower = TechnicalAnalysis.atrBand(data, coeff)
        if key == ATR_BAND_UPPER:
            array = upper
        else:
            array = lower
    elif key == ATR_BREAKUP_SIGNAL:
        array = TechnicalAnalysis.breakSignal(data, ATR_BAND_UPPER, True)
    elif key == ATR_BREAKDOWN_SIGNAL:
        array = TechnicalAnalysis.breakSignal(data, ATR_BAND_LOWER, False)
    elif key == MA_TREND_BAND:
        threshold = params[THRESHOLD]
        ma_keys = params[MA_KEYS]
        mas = [data[key] for key in ma_keys]
        if len(mas) != 3:
            raise Exception('Bad MA_TREND_BAND parameter')
        array = TechnicalAnalysis.maTrendBand(data[OPEN], data[HIGH], data[LOW], data[CLOSE], mas, threshold)
    elif key == PATTERN_MATCH:
        source = params[SOURCE]
        signal = data[source]
        patterns = params[PATTERNS]
        array = TechnicalAnalysis.patternMatching(signal, patterns)
    else:
        return None
    
    if name is None:
        name = key
    if should_set:
        data[name] = array
    return array

# -----
def isKeys(dic, keys):
    for key in keys:
        if not key in dic.keys():
            return False
    return True

def sma(key, dic, begin, end):
    params = {WINDOW: 14}
    return seqIndicator(key, dic, begin, end, params)

def atr(key, dic, begin, end):
    params = {WINDOW: 14}
    return seqIndicator(key, dic, begin, end, params)

def atrband(key, dic, begin, end):
    if not isKeys(dic, [ATR]):
        return False
    params ={WINDOW:14, COEFF: 1.0}
    return seqIndicator(key, dic, begin, end, params)

def atrbreak(key, dic, begin, end):
    if not isKeys(dic, [ATR_BAND_LOWER, ATR_BAND_UPPER]):
        return False
    params = {WINDOW: 14}
    return seqIndicator(key, dic, begin, end, params)