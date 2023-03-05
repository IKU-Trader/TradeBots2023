# -*- coding: utf-8 -*-
"""
Created on Tue Nov 29 11:21:36 2022

@author: IKU-Trader
"""

import sys
sys.path.append('../')

import MetaTrader5 as mt5
from mt5_const import mt5_const as const
from TimeUtils import TimeUtils
from datetime import datetime


class Order:
    typ = int 
    BuyEntry: typ = 0
    SellEntry: typ = 1
    
    kind = int 
    MarketOrder: kind = 0
    Limit: kind = 1
    Stop: kind = 2
    
    def __init__(self, symbol, lot, price, typ: typ, kind, magic_number):
        self.symbol = symbol
        if typ == Order.BuyEntry:
            if kind == Order.MarketOrder:
                self.type = mt5.ORDER_TYPE_BUY
            elif kind == Order.Limit:
                self.type = mt5.ORDER_TYPE_BUY_LIMIT
            elif kind == Order.Stop:
                self.type = mt5.ORDER_TYPE_BUY_STOP
        elif typ == Order.SellEntry:
            if kind == Order.MarketOrder:
                self.type = mt5.ORDER_TYPE_SELL
        self.lot = lot
        self.price = price
        self.magic_number = magic_number
        
class BuyMarketOrder(Order):
    def __init__(self, symbol, lot, price):
        super().__init__(symbol, lot, price, 
                         Order.BuyEntry, Order.MarketOrder, 1000)

 
class PyMT5:
    def __init__(self, market: str):
        self.market = market
        if not mt5.initialize():
            print("initialize() failed")
            mt5.shutdown()
        print('Version: ', mt5.version())
    
    def close(self):
        mt5.shutdown()
    
    def convert(self, data: list):
        if data is None:
            return ([], {})
        timeJst = []
        timestamp = []
        arrays = []
        for i in range(5):
            arrays.append([])
        ohlcv = []
        for d in data:
            values = list(d)
            jst = TimeUtils.timestamp2jst(values[0])
            timeJst.append(jst)
            timestamp.append(jst.timestamp())
            for i in range(5):
                if i == 4:
                    j = 7
                else:
                    j = i + 1
                arrays[i].append(values[j])
            ohlcv.append([values[1], values[2], values[3], values[4]])
        dic = {}
        dic[const.TIMEJST] = timeJst
        dic[const.TIMESTAMP] = timestamp
        dic[const.OPEN] = arrays[0]
        dic[const.HIGH] = arrays[1]
        dic[const.LOW] = arrays[2]
        dic[const.CLOSE] = arrays[3]
        dic[const.VOLUME] = arrays[4]
        return (ohlcv, dic)
     
    def download(self, timeframe: str, size: int=99999):
        d = mt5.copy_rates_from_pos(self.market, const.TIMEFRAME[timeframe][0] , 0, size) 
        return self.convert(d)

    def downloadRange(self, timeframe: str, begin_jst: datetime, end_jst: datetime):
        utc_from = self.jst2serverTime(begin_jst)
        utc_to = self.jst2serverTime(end_jst)
        d = mt5.copy_rates_range(self.stock, const.TIMEFRAME[timeframe][0] , utc_from, utc_to) 
        return self.convert(d)
    
    def downloadTicks(self, timeframe: str, from_jst: datetime, size: int=100000):
        utc_from = self.jst2serverTime(from_jst)
        d = mt5.copy_ticks_from(self.stock, const.TIMEFRAME[timeframe][0] , utc_from, size, mt5.COPY_TICKS_ALL) 
        return self.convert(d)
    
    def accountInfo(self):
        dic = {}
        info = mt5.account_info()
        if info is None:
            print(f"Retreiving account information failed")
            return dic
        dic['balance'] = info.balance
        dic['credit'] = info.credit
        dic['profit'] = info.profit
        dic['equity'] = info.equity
        dic['margin'] = info.margin
        dic['margin_free'] = info.margin_free
        dic['margin_level'] = info.margin_level
        dic['margin_so_call'] = info.margin_so_call
        dic['currency'] = info.currency                
        return dic


    def positions(self, symbol: str):
        pos = mt5.positions_get(group='*'+symbol+'*')
        buy_positions = []
        sell_positions = []
        for p in pos:
            order_type = p[5]
            profit = p[15]
            lot = [9]
            price = [10]
            if order_type == 0: # buy
                buy_positions.append([lot, profit, price])
            elif order_type == 1: # sellポジションの場合
                sell_positions.append([lot, profit, price])
        return (buy_positions, sell_positions)
    
    
    def order(self, request: Order):
        request = {
                'symbol': request.symbol,
                'action': mt5.TRADE_ACTION_DEAL,
                'type': request.type,
                'volume': request.lot,
                'price': request.price,
                'deviation': request.slippage,
                'comment': 'first_buy',
                'magic': magic_number,
                'type_time': mt5.ORDER_TIME_GTC, # 注文有効期限
                'type_filling': mt5.ORDER_FILLING_IOC, # 注文タイプ
                }
        result = mt5.order_send(request)


# -----
    
def test(size):
    server = PyMT5('USDJPY')
    
    info = server.accountInfo()
    print(info)
    
    positions = server.positions('DJI')
    print(positions)
    
    ohlcv, dic =  server.download('M1', size=size) 
    print(ohlcv)
    print(dic[const.TIMEJST])

if __name__ == "__main__":
    test(3)