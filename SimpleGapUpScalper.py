import time
from ib_insync.contract import Index, Option, Stock
from ib_insync.ib import IB
from datetime import datetime
import pandas as pd
from ib_insync import Order
import random
import traceback

ticker_dict = {}

# Logging into Interactive Broker TWS
ib = IB()
ib.connect('127.0.0.1', 7497, clientId=random.randint(0, 300))

class GapUpScalper_Driver():

    def get_percent(self, first, second):
        if first == 0 or second == 0:
            return 0
        else:
            percent = first / second * 100
        return percent

    def sell_stock(self):

       ib.reqGlobalCancel()

       ticker = ib.positions()[0]
       qty = [v.position for v in ib.positions()][0]

       ticker_contract = Stock(ticker, 'SMART', 'USD')

       order = Order(orderId=15, action='Sell', orderType='MKT', totalQuantity=qty)

       ib.placeOrder(ticker_contract, order)

       print('Sold ' + str(ticker) +  "!")

       time.sleep(10)

    def buy_stock(self, ticker, premarket_high):

        now = str(datetime.now().time())  # time object

        TimeNow = pd.to_datetime(now).tz_localize('America/New_York')
        EndTime = pd.to_datetime("15:30").tz_localize('America/New_York')

        if TimeNow > EndTime:

           ticker_contract = Stock(ticker, 'SMART', 'USD')

           [ticker_close] = ib.reqTickers(ticker_contract)

           print("ticker: ", ticker_close)

           acc_vals = float([v.value for v in ib.accountValues() if v.tag == 'CashBalance' and v.currency == 'USD'][0])

           limit_price = float(str(round(premarket_high * 1.005, 2)))
           take_profit = float(str(round(premarket_high * 1.105, 2)))
           stop_loss_price = float(str(round(premarket_high * 0.985, 2)))

           percent_of_acct_to_trade = 0.05

           qty = (acc_vals // limit_price) * percent_of_acct_to_trade
           qty = round(qty)

           pct_difference = round(self.get_percent((qty * limit_price), acc_vals), 2)

           print('\nYou bought ' + str(qty) + ' shares of ' + str(ticker) +
                 ' for a total of $' + str(round(qty * limit_price)) + ' USD' +
                 ' which is ' + str(pct_difference) + '% of your account ')

           print('\nYou set a buy limit order for $' + str(limit_price) + ', a take profit at $'
                 + str(take_profit) + ' and a stop loss at $' + str(stop_loss_price))

           entry_order = ib.bracketOrder(
               'BUY',
               qty,
               limitPrice=limit_price,
               takeProfitPrice=take_profit,
               stopLossPrice=stop_loss_price
           )

           for o in entry_order:
               ib.placeOrder(ticker_contract, o)
               ib.oneCancelsAll([o for o in entry_order], 'group', 1)

           time.sleep(15)

           return qty
