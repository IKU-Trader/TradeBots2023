# -*- coding: utf-8 -*-
import sys
sys.path.append("./TA")

import pandas as pd
import numpy as np
import copy
from datetime import datetime, timedelta
from const import TIME, OPEN, HIGH, LOW, CLOSE, VOLUME
from const import TimeUnit, UNIT_MINUTE, UNIT_HOUR, UNIT_DAY
from time_util import TIMEZONE_TOKYO
from Utils import Utils
from STA import indicator, arrays2dic, seqIndicator
from STA import SMA, WINDOW, MA_TREND_BAND, THRESHOLD, MA_KEYS, PATTERNS, SOURCE, PATTERN_MATCH
from STA import UPPER_TREND, UPPER_SUB_TREND, UPPER_DIP, LOWER_TREND, LOWER_SUB_TREND, LOWER_DIP, NO_TREND
from MathArray import MathArray

class DataBuffer:
    # tohlcv: arrays ( time array, open array, ...)
    def __init__(self, tohlcv:[[]], ta_params: [], interval_minutes: int):
        self.ta_params = ta_params
        self.interval_minutes = interval_minutes
        tohlcv_arrays, tmp_candles = self.resample(tohlcv, interval_minutes, UNIT_MINUTE)
        self.tmp_candles = tmp_candles
        self.invalid_candle = None
        dic = self.arrays2Dic(tohlcv_arrays)
        self.addIndicator(dic)
        self.dic = dic
        
    def tohlcvDic(self):
        return self.dic
    
    def candles(self):
        return self.dic2Candles(self.dic)
    
    def tohlcvArrays(self):
        return self.dic2Arrays(self.dic)
    
    def size(self):
        return len(self.dic)
    
    
    def lastTime(self):
        if self.size() > 0:
            return self.data[TIME][-1]
        else:
            return None
        
    def deltaTime(self):
        if self.size() > 1:
            time = self.data[TIME]
            dt = time[1] - time[0]
            return dt
        else:
            return None
        
    def needSize(self):
        t1 = datetime.now(TIMEZONE_TOKYO)
        t0 = self.lastTime()
        n = (t1 - t0) / self.deltaTime()
        n = int(n + 0.5) +1
        return n
    
    # dic: tohlcv+ array dict
    def addIndicator(self, dic: dict):
        for name, value in self.ta_params.items():
            method, param = value 
            indicator(dic, method, param, name=name)
        return dic

    def updateSeqIndicator(self, dic: dict, begin: int, end: int):
        for name, [key, param] in self.ta_params.items():
            seqIndicator(dic, key, begin, end, param, name=name)
        return dic
    
    # dic: tohlcv+ array dict
    def deleteLastData(self, dic):
        keys, arrays = dic2Arrays(dic)
        out = {}
        for key, array in zip(keys, arrays):
            out[key] = array[:-1]
        return out
    
    # candles: tohlcv array
    def update(self, candles):
        self.invalid_candle = candles[-1]
        valid_candles = candles[:-1]
        new_candles, tmp_candles = self.compositCandle(valid_candles)
        self.tmp_candles = tmp_candles
        m = len(new_candles)
        if m > 0:
            begin = len(self.dic[TIME])        
            end = begin + m - 1
            self.merge(self.dic, new_candles)
            self.updateSeqIndicator(self.dic, begin, end)
    
    def compositCandle(self, candles):
        tmp_candles = self.tmp_candles.copy()
        new_candles = []
        last_time = self.dic[TIME][-1]
        for candle  in candles:
            t = candle[0]
            if t <= last_time:
                continue
            t_round =  self.roundTime(t, self.interval_minutes, UNIT_MINUTE)
            if t == t_round:    
                tmp_candles.append(candle)
                c = self.candlePrice(t_round, tmp_candles)
                new_candles.append(c)
                tmp_candles = []
            else:
                if len(tmp_candles) > 0:
                    if t > tmp_candles[-1][0]:
                        tmp_candles.append(candle)
                else:
                    tmp_candles.append(candle)
        return new_candles, tmp_candles
        
    def temporary(self):
        tmp_candles = copy.deepcopy(self.tmp_candles)
        if self.invalid_candle is not None:
            tmp_candles.append(self.invalid_candle)
        if len(tmp_candles) == 0:
            return self.dic[TIME][-1], self.dic.copy()
        t = tmp_candles[-1][0]
        t_round =  self.roundTime(t, self.interval_minutes, UNIT_MINUTE)
        new_candle = self.candlePrice(t_round, tmp_candles)
        tmp_dic = copy.deepcopy(self.dic)
        begin = len(tmp_dic[TIME])
        self.merge(tmp_dic, [new_candle])        
        end = len(tmp_dic[TIME]) - 1
        self.updateSeqIndicator(tmp_dic, begin, end)
        return tmp_candles[-1][0], tmp_dic

    def merge(self, dic: dict, candles):
        index = {TIME: 0, OPEN: 1, HIGH: 2, LOW: 3, CLOSE: 4, VOLUME: 5}
        n = len(candles)
        blank = MathArray.full(n, np.nan)
        for key, array in dic.items():
            try:
                i = index[key]
                a = [candle[i] for candle in candles]
                array += a
            except:
                array += blank.copy()
        return

    def roundTime(self, time: datetime, interval: int, unit: TimeUnit):
        zone = time.tzinfo
        if unit == UNIT_MINUTE:
            t = datetime(time.year, time.month, time.day, time.hour, 0, 0, tzinfo=zone)
        elif unit == UNIT_HOUR:
            t = datetime(time.year, time.month, time.day, 0, 0, 0, tzinfo=zone)
        elif unit == UNIT_DAY:
            t = datetime(time.year, time.month, time.day, 0, 0, 0, tzinfo=zone)
            return t
        if t == time:
            return t
        while t < time:
            if unit == UNIT_MINUTE:
                t += timedelta(minutes=interval)
            elif unit == UNIT_HOUR:
                t += timedelta(hours=interval)
        return t

    def candlePrice(self, time:datetime, tohlcv_list:[]):
        m = len(tohlcv_list[0])
        n = len(tohlcv_list)
        o = tohlcv_list[0][1]
        c = tohlcv_list[-1][4]
        h_array = [tohlcv_list[i][2] for i in range(n)]
        h = max(h_array)
        l_array = [tohlcv_list[i][3] for i in range(n)]
        l = min(l_array)
        if m > 4:
            v_array = [tohlcv_list[i][5] for i in range(n)]
            v = sum(v_array)
            return [time, o, h, l, c, v]
        else:
            return [time, o, h, l, c]
    
    # tohlcv: tohlcv arrays
    def resample(self, tohlcv: [], interval: int, unit: TimeUnit):        
        time = tohlcv[0]
        n = len(time)
        op = tohlcv[1]
        hi = tohlcv[2]
        lo = tohlcv[3]
        cl = tohlcv[4]
        if len(tohlcv) > 5:
            vo = tohlcv[5]
            is_volume = True
        else:
            is_volume = False
        data_list = []
        candles = []
        current_time = None
        for i in range(n):
            t_round = self.roundTime(time[i], interval, unit)
            if is_volume:
                values = [time[i], op[i], hi[i], lo[i], cl[i], vo[i]]
            else:
                values = [time[i], op[i], hi[i], lo[i], cl[i]]
            if current_time is None:
                current_time = t_round
                data_list = [values]
            else:
                if t_round == current_time:
                    data_list.append(values)
                else:
                    candle = self.candlePrice(current_time, data_list)
                    candles.append(candle)
                    data_list = [values]
                    current_time = t_round
        if len(data_list) == interval:
            candle = self.candlePrice(current_time, data_list)
            candles.append(candle)
            data_list = []
        return self.candles2Arrays(candles), data_list

    def arrays2Candles(self, tohlcvArrays:[]):
        out = []
        n = len(tohlcvArrays[0])
        for i in range(n):
            d = [array[i] for array in tohlcvArrays]
            out.append(d)
        return out

    def candles2Arrays(self, candles:[]):
        n = len(candles)
        m = len(candles[0])
        arrays = []
        for i in range(m):
            array = [candles[j][i] for j in range(n)]
            arrays.append(array)
        return arrays

    def dic2Candles(self, dic):
        arrays = [dic[TIME], dic[OPEN], dic[HIGH], dic[LOW], dic[CLOSE]]
        try:
            arrays.append(dic[VOLUME])
        except:
            pass
        out = []
        for i in range(len(arrays[0])):
            d = [] 
            for array in arrays:
                d.append(array[i])
            out.append(d)
        return out
            
    def arrays2Dic(self, tohlcvArrays:[]):
        dic = {}
        dic[TIME] = tohlcvArrays[0]
        dic[OPEN] = tohlcvArrays[1]
        dic[HIGH] = tohlcvArrays[2]
        dic[LOW] = tohlcvArrays[3]
        dic[CLOSE] = tohlcvArrays[4]
        if len(tohlcvArrays) > 5:
            dic[VOLUME] = tohlcvArrays[5]
        return dic