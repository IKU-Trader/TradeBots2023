
How = int
NEXT_OPEN: How = 1
NEXT_CLOSE: How = 2
WAIT_PRICE: How = 3
INSTANT: How = 4

class TradeRule:
    def __init__(self):
        self.entry = NEXT_OPEN
        self.exit = INSTANT
        pass
