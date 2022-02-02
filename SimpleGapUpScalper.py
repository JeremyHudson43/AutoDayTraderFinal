import time
from ib_insync.contract import Stock
from ib_insync import Order
import sys
from math import floor
import pandas as pd
from datetime import datetime

class GapUpScalper_Driver():

    def seconds_until_end_of_minute(self):
        dt = datetime.now()
        return 60 - dt.second

    def get_percent(self, first, second):
        if first == 0 or second == 0:
            return 0
        else:
            percent = first / second * 100
        return percent

    def sell_stock(self, ib, qty, ticker):

       ib.reqGlobalCancel()

       if qty > 0:

           ticker_contract = Stock(ticker, 'SMART', 'USD')

           order = Order(orderId=27, action='Sell', orderType='MKT', totalQuantity=qty)

           ib.placeOrder(ticker_contract, order)

           print('\nSold ' + str(ticker) +  " at the end of the day!")

           time.sleep(10)

           sys.exit(0)

    def check_second_breakout(self, ticker, ib, second_breakout_price):

        seconds_left = self.seconds_until_end_of_minute()
        time.sleep(seconds_left)

        ticker_contract = Stock(ticker, 'SMART', 'USD')
        [ticker_close] = ib.reqTickers(ticker_contract)

        print('\nChecking for ' + ticker + '\'s second breakout at: $' + str(round(second_breakout_price, 2)) + "...")
        print(ticker + "\'s current price: $" + str(round(ticker_close.marketPrice(), 2)))

        if ticker_close.marketPrice() >= second_breakout_price:

            time.sleep(self.seconds_until_end_of_minute() + 5)

            market_data = pd.DataFrame(
                ib.reqHistoricalData(
                    ticker_contract,
                    endDateTime='',
                    durationStr='60 S',
                    barSizeSetting='1 min',
                    whatToShow="TRADES",
                    formatDate=1,
                    useRTH=True
                ))

            if market_data['Close'].max() >= second_breakout_price:

                resistance_broke_two = True
                print("\nResistance Two Broke at $" + str(round(ticker_close.marketPrice(), 2)) + "!")

                breakout_price = ticker_close.marketPrice()

                return ticker, breakout_price, resistance_broke_two
        else:
            return ticker, 0, False

    def check_first_breakout(self, ticker, breakout_area, ib):
        ticker_contract = Stock(ticker, 'SMART', 'USD')

        [ticker_close] = ib.reqTickers(ticker_contract)

        breakout_area = round(breakout_area * 1.005, 2)

        limit_market_difference = 100 - self.get_percent(ticker_close.marketPrice(), breakout_area)

        print("Current " + ticker + " Price: $", round(ticker_close.marketPrice(), 2))
        print("Difference", str(round(abs(limit_market_difference), 2)) + "%")
        print('Checking for first breakout...')

        resistance_broke_one = False

        if ticker_close.marketPrice() >= breakout_area:

            seconds_left = self.seconds_until_end_of_minute()

            time.sleep(seconds_left)

            market_data = pd.DataFrame(
                ib.reqHistoricalData(
                    ticker_contract,
                    endDateTime='',
                    durationStr='300 S',
                    barSizeSetting='1 min',
                    whatToShow="TRADES",
                    formatDate=1,
                    useRTH=True
                ))

            highest_price = market_data['high'].max()

            resistance_broke_one = True

            print("\nResistance One Broke at $" + str(round(ticker_close.marketPrice(), 2)) + " for " + ticker + "!")

            return ticker, highest_price, resistance_broke_one

        else:
            return ticker, 0, resistance_broke_one

    def buy_stock(self, ticker, ib):

       ticker_contract = Stock(ticker, 'SMART', 'USD')

       [ticker_close] = ib.reqTickers(ticker_contract)

       current_price = ticker_close.marketPrice()

       acc_vals = float([v.value for v in ib.accountValues() if v.tag == 'CashBalance' and v.currency == 'USD'][0])

       percent_of_acct_to_trade = 0.5

       qty = (acc_vals // current_price) * percent_of_acct_to_trade
       qty = floor(qty)

       limit_price = float(round(current_price, 2))
       take_profit = float(round(current_price * 1.10, 2))
       stop_loss_price = float(round(current_price * 0.98, 2))

       print(limit_price, take_profit, stop_loss_price)

       buy_order = ib.bracketOrder(
           'BUY',
           qty,
           limitPrice=limit_price,
           takeProfitPrice=take_profit,
           stopLossPrice=stop_loss_price
       )

       for o in buy_order:
           ib.placeOrder(ticker_contract, o)

       pct_difference = round(self.get_percent((qty * ticker_close.marketPrice()), acc_vals), 2)

       print('\nYou bought ' + str(qty) + ' shares of ' + str(ticker) +
             ' for a total of $' + str(round(qty * ticker_close.marketPrice())) + ' USD' +
             ' which is ' + str(pct_difference) + '% of your account ')

       purchased = True

       return purchased, qty, ticker
