import time
from ib_insync.contract import Index, Option, Stock
from ib_insync.ib import IB
from datetime import datetime
import pandas as pd
from ib_insync import Order
import random

ticker_dict = {}

# Logging into Interactive Broker TWS
ib = IB()


class GapUpScalper_Driver():

    def check_for_breakout(self, ticker, high):

        ib.connect('127.0.0.1', 7497, clientId=random.randint(0, 300))

        stock_brokeout = False

        while not stock_brokeout:

            ticker_obj = Stock(ticker, 'SMART', 'USD')

            [ticker] = ib.reqTickers(ticker_obj)

            current_stock_value = ticker.marketPrice()

            print('\nTicker: ', ticker_obj.symbol)
            print('Current Stock Value: ', current_stock_value)
            print('Premarket High: ', high)

            # if current stock value is greater than premarket high, add to list of stocks that broke out
            if current_stock_value > high:
                stock_brokeout = True
                return stock_brokeout, ticker_obj.symbol

            time.sleep(5)

            ib.disconnect()


    def sell_stock(self, ticker):

       ib.connect('127.0.0.1', 7497, clientId=random.randint(0, 300))

       ib.reqGlobalCancel()

       ticker_contract = Stock(ticker, 'SMART', 'USD')

       qty = [v.position for v in ib.positions()][0]

       order = Order(orderId=15, action='Sell', orderType='MKT', totalQuantity=qty)

       ib.placeOrder(ticker_contract, order)

       print('Sold ' + str(ticker) +  "!")

       time.sleep(10)

       ib.disconnect()


    def buy_stock(self, ticker, premarket_high):

        now = str(datetime.now().time())  # time object

        TimeNow = pd.to_datetime(now).tz_localize('America/New_York')
        EndTime = pd.to_datetime("15:30").tz_localize('America/New_York')

        if TimeNow < EndTime:

           ib.connect('127.0.0.1', 7497, clientId=random.randint(0, 300))

           ticker_contract = Stock(ticker, 'SMART', 'USD')

           [ticker_close] = ib.reqTickers(ticker_contract)

           print("ticker: ", ticker_close)

           Current_Ticker_Value = ticker_close.marketPrice()

           acc_vals = float([v.value for v in ib.accountValues() if v.tag == 'CashBalance' and v.currency == 'USD'][0])

           qty = (acc_vals // Current_Ticker_Value) * 0.05

           qty = round(qty)

           limit_price = float(str(round(premarket_high * 1.005, 2)))
           take_profit = float(str(round(premarket_high * 1.105, 2)))
           stop_loss_price = float(str(round(premarket_high * 0.985, 2)))

           entry_order = ib.bracketOrder(
               'BUY',
               qty,
               limitPrice=limit_price,
               takeProfitPrice=take_profit,
               stopLossPrice=stop_loss_price
           )

           for o in entry_order:
               ib.placeOrder(ticker_contract, o)

           ib.disconnect()
