import time
from ib_insync.contract import Stock
from ib_insync import Order
import sys
from math import floor

class GapUpScalper_Driver():

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

           print('\nSold ' + str(ticker) +  "!")

           time.sleep(10)

           sys.exit(0)

    def check_second_breakout(self, ticker, ib, resistance_price):

        ticker_contract = Stock(ticker, 'SMART', 'USD')
        [ticker_close] = ib.reqTickers(ticker_contract)

        time.sleep(300)

        resistance_broke_two = False

        while not resistance_broke_two:
            time.sleep(5)

            print('\nChecking for second breakout...')
            print("Resistance Price", resistance_price)
            print("Current Price", ticker_close.marketPrice())

            if ticker_close.marketPrice() >= resistance_price:
                resistance_broke_two = True
                print("\nResistance Two Broke at $" + str(ticker_close.marketPrice()) + "!")

                return ticker, resistance_price, resistance_broke_two

    def check_first_breakout(self, ticker, premarket_high, ib):
        ticker_contract = Stock(ticker, 'SMART', 'USD')

        [ticker_close] = ib.reqTickers(ticker_contract)

        premarket_high = float(str(round(premarket_high, 2)))

        limit_market_difference = 100 - self.get_percent(ticker_close.marketPrice(), premarket_high)

        print("Current Price:", ticker_close.marketPrice())
        print("Difference", str(round(abs(limit_market_difference), 2)) + "%")
        print('Checking for first breakout...')

        resistance_broke_one = False

        if ticker_close.marketPrice() >= premarket_high * 0.905:
            resistance_broke_one = True
            print("\nResistance One Broke at $" + str(ticker_close.marketPrice()) + "!")

            resistance = ticker_close.marketPrice()

            return ticker, resistance, resistance_broke_one

        else:
            return ticker, 0, resistance_broke_one

    def buy_stock(self, ticker, resistance, multiplier, ib):

       ticker_contract = Stock(ticker, 'SMART', 'USD')
       [ticker_close] = ib.reqTickers(ticker_contract)

       acc_vals = float([v.value for v in ib.accountValues() if v.tag == 'CashBalance' and v.currency == 'USD'][0])

       percent_of_acct_to_trade = 0.03

       qty = (acc_vals // resistance) * percent_of_acct_to_trade
       qty = floor(qty)

       buy_order = Order(orderId=5 * multiplier, action='BUY', orderType='MKT', totalQuantity=qty)

       ib.placeOrder(ticker_contract, buy_order)

       pct_difference = round(self.get_percent((qty * ticker_close.marketPrice()), acc_vals), 2)

       print('\nYou bought ' + str(qty) + ' shares of ' + str(ticker) +
             ' for a total of $' + str(round(qty * ticker_close.marketPrice())) + ' USD' +
             ' which is ' + str(pct_difference) + '% of your account ')

       sell_order = Order(orderId=10 * multiplier, action='Sell', orderType='TRAIL',
                          trailingPercent=2.0, totalQuantity=qty)

       ib.placeOrder(ticker_contract, sell_order)

       purchased = True

       return purchased, qty, ticker
