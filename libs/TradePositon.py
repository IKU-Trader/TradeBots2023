from datetime import datetime

TradeKind = int
SHORT: TradeKind = -1
LONG: TradeKind = 1

class TradePosition:
    def __init__(self, kind: TradeKind, time: datetime, price:float, stop_price: float):
        self.kind = kind
        self.open_price = price
        self.open_time = time
        self.stop_price = stop_price
        self.is_close = False
        pass

    def close(self, time: datetime, price: float):
        self.close_price = price
        self.close_time = time
        self.profit = price - self.open_price
        if self.kind == SHORT:
            self.profit *= -1.0
        self.profit_percent = self.profit / self.open_price * 100.0
        self.is_close = True

    def shouldStop(self, price):
        if self.kind == LONG:
            return price <= self.stop_price
        elif self.kind == SHORT:
            return price >= self.stop_price
