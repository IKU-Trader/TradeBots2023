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
    Kind = int 
    EntryBuy: Kind = 0
    EntrySell: Kind = 1
    CloseBuy: Kind = 2
    CloseSell: Kind = 3
    CancelOrder: Kind = 4
    
    How = int 
    MarketOrder: How = 0
    Limit: How = 1
    Stop: How = 2
    
    def __init__(self,  symbol: str,
                         lot: int, 
                         price: float, 
                         order_kind: Kind, 
                         order_how: How,
                         slippage: int,
                         stoploss: float,
                         takeprofit: float,
                         magic_number: int,
                         ticket: int):
        self.symbol = symbol
        if order_kind == Order.EntryBuy:
            if order_how == Order.MarketOrder:
                self.action = mt5.TRADE_ACTION_DEAL
                self.type = mt5.ORDER_TYPE_BUY
            elif order_how == Order.Limit:
                self.action = mt5.TRADE_ACTION_PENDING
                self.type = mt5.ORDER_TYPE_BUY_LIMIT
            elif order_how == Order.Stop:
                self.action = mt5.TRADE_ACTION_PENDING
                self.type = mt5.ORDER_TYPE_BUY_STOP
        elif order_kind == Order.EntrySell:
            if order_how == Order.MarketOrder:
                self.action = mt5.TRADE_ACTION_DEAL
                self.type = mt5.ORDER_TYPE_SELL
            elif order_how == Order.Limit:
                self.action = mt5.TRADE_ACTION_PENDING
                self.type = mt5.ORDER_TYPE_SELL_LIMIT
            elif order_how == Order.Stop:
                self.action = mt5.TRADE_ACTION_PENDING
                self.type = mt5.ORDER_TYPE_SELL_STOP
        elif order_kind == Order.CloseSell:
            if order_how == Order.MarketOrder:
                self.action = mt5.TRADE_ACTION_DEAL
                self.type = mt5.ORDER_TYPE_SELL
        elif order_kind == Order.CloseBuy:
            if order_how == Order.MarketOrder:
                self.action = mt5.TRADE_ACTION_DEAL
                self.type = mt5.ORDER_TYPE_BUY            
        self.ticket = ticket
        self.lot = lot
        self.price = price
        self.magic_number = magic_number
        self.slippage = slippage
        self.stoploss = stoploss
        self.takeprofit = takeprofit

class BuyMarketOrder(Order):
    def __init__(self, symbol, lot, slippage, stoploss, takeprofit):
        price = mt5.symbol_info_tick(symbol).ask
        if stoploss is not None:
            sl = price - abs(stoploss)
        else:
            sl = None
        if takeprofit is not None:
            tp = price + abs(takeprofit)
        else:
            tp = None
        super().__init__(symbol,
                         lot,
                         price,
                         Order.EntryBuy,
                         Order.MarketOrder,
                         slippage,
                         sl,
                         tp,
                         1000,
                         None)

class SellMarketOrder(Order):
    def __init__(self, symbol, lot, slippage, stoploss, takeprofit):
        price = mt5.symbol_info_tick(symbol).ask
        if stoploss is not None:
            sl = price + abs(stoploss)
        else:
            sl = None
        if takeprofit is not None:
            tp = price - abs(takeprofit)
        else:
            tp = None
        super().__init__(symbol,
                         lot,
                         price,
                         Order.EntrySell,
                         Order.MarketOrder,
                         slippage,
                         sl,
                         tp,
                         2001,
                         None)
        
class BuyLimitOrder(Order):
    def __init__(self, symbol, lot, price, slippage, stoploss, takeprofit):
        if stoploss is not None:
            sl = price - abs(stoploss)
        else:
            sl = None
        if takeprofit is not None:
            tp = price + abs(takeprofit)
        else:
            tp = None
        super().__init__(symbol,
                         lot,
                         price,
                         Order.EntryBuy,
                         Order.Limit,
                         slippage,
                         sl,
                         tp,
                         1002,
                         None)
        
class SellLimitOrder(Order):
     def __init__(self, symbol, lot, price, slippage, stoploss, takeprofit):
         if stoploss is not None:
             sl = price + abs(stoploss)
         else:
             sl = None
         if takeprofit is not None:
             tp = price - abs(takeprofit)
         else:
             tp = None
         super().__init__(symbol,
                          lot,
                          price,
                          Order.EntrySell,
                          Order.Limit,
                          slippage,
                          sl,
                          tp,
                          2002,
                          None) 
         
class BuyStopOrder(Order):
    def __init__(self, symbol, lot, price, slippage, stoploss, takeprofit):
        if stoploss is not None:
            sl = price - abs(stoploss)
        else:
            sl = None
        if takeprofit is not None:
            tp = price + abs(takeprofit)
        else:
            tp = None
        super().__init__(symbol,
                         lot,
                         price,
                         Order.EntryBuy,
                         Order.Stop,
                         slippage,
                         sl,
                         tp,
                         1003,
                         None)

class SellStopOrder(Order):
    def __init__(self, symbol, lot, price, slippage, stoploss, takeprofit):
        if stoploss is not None:
            sl = price - abs(stoploss)
        else:
            sl = None
        if takeprofit is not None:
            tp = price + abs(takeprofit)
        else:
            tp = None
        super().__init__(symbol,
                         lot,
                         price,
                         Order.EntrySell,
                         Order.Stop,
                         slippage,
                         sl,
                         tp,
                         2003,
                         None)        
        
class CloseBuyPostionMarketOrder(Order):
    def __init__(self, symbol, lot, ticket):
        price = mt5.symbol_info_tick(symbol).bid
        super().__init__(symbol,
                         lot,
                         price,
                         Order.EntrySell,
                         Order.MarketOrder,
                         None,
                         None,
                         None,
                         3001,
                         ticket)    
    
class CloseSellPostionMarketOrder(Order):
    def __init__(self, symbol, lot, ticket):
        price = mt5.symbol_info_tick(symbol).bid
        super().__init__(symbol,
                         lot,
                         price,
                         Order.EntryBuy,
                         Order.MarketOrder,
                         None,
                         None,
                         None,
                         3001,
                         ticket)        
    
        
class PyMT5:
    def __init__(self):
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
            print("Retreiving account information failed")
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

    def checkSymbol(self, symbol: str):
        info = mt5.symbol_info(symbol)
        if info is None:
            return False
        else:
            return True

    def positions(self, symbol: str):
        pos = mt5.positions_get(group='*'+symbol+'*')
        buy_positions = []
        sell_positions = []
        for p in pos:
            order_type = p[5]
            profit = p[15]
            lot = [9][0]
            price = [10][0]
            if order_type == 0: # buy
                buy_positions.append([lot, profit, price])
            elif order_type == 1: # sellポジションの場合
                sell_positions.append([lot, profit, price])
        return (buy_positions, sell_positions)
      
    def position(self, ticket):
        dic = {}
        pos = mt5.positions_get(ticket=ticket)
        if pos is None:
            return dic
        p = pos[0]
        dic['price_open'] = p.price_open
        dic['price_current'] = p.price_current
        dic['swap'] = p.swap
        dic['profit'] = p.profit
        return dic

    def buyMarketOrder(self, symbol: str, lot:int, slippage=None, stoploss=None, takeprofit=None):
        order = BuyMarketOrder(symbol, lot, slippage, stoploss, takeprofit)
        return self.sendOrder(order)
        
    def sellMarketOrder(self, symbol: str, lot:int, slippage=None, stoploss=None, takeprofit=None):
        order = SellMarketOrder(symbol, lot, slippage, stoploss, takeprofit)
        return self.sendOrder(order)
            
    
        
        
    def sendOrder(self, order: Order):
        request = {
                    'action': order.action,
                    'symbol': order.symbol,                
                    'type': order.type,
                    'volume': order.lot,
                    'price': order.price,
                    'comment': 'By python API',
                    'magic': order.magic_number,
                    'type_time': mt5.ORDER_TIME_GTC,
                    'type_filling': mt5.ORDER_FILLING_IOC,
                    }
        if order.ticket is not None:
            request['position'] = order.ticket
        if order.slippage is not None:
            request['deviation'] = order.slippage
        if order.stoploss is not None:
            request['sl'] = order.stoploss
        if order.takeprofit is not None:
            request['tp'] = order.takeprofit       
            
        result = mt5.order_send(request)
        dic = {}
        dic['retcode'] = result.retcode
        dic['ticket'] = result.order
        dic['volume'] = result.volume
        dic['price'] = result.price

        return ((result.retcode == 10009), dic) 

    def closeBuyPositionMarketOrder(self, symbol: str, lot: int, ticket: int):    
        order = CloseBuyPostionMarketOrder(symbol, lot, ticket)
        return self.sendOrder(order)
    
    def closeSellPositionMarketOrder(self, symbol: str, lot: int, ticket: int):    
        order = CloseSellPostionMarketOrder(symbol, lot, ticket)
        return self.sendOrder(order)

# -----
    
def test(size):
    server = PyMT5()
    
    info = server.accountInfo()
    print(info)
    
    positions = server.positions('USDJPY')
    print(positions)
    
    ohlcv, dic =  server.download('M1', size=size) 
    print(ohlcv)
    print(dic[const.TIMEJST])

def test1():
    server = PyMT5()
    ret = server.buyMarketOrder('USDJPY', 0.05)
    print(ret)
    
def test2():
    server = PyMT5()
    ret = server.closeBuyPositionMarketOrder('USDJPY', 0.05, 1185114)
    print(ret)
    
if __name__ == "__main__":
    test2()