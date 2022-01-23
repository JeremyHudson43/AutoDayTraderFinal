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

    def check_second_breakout(self, ticker, ib):

        highest_price = 0
        resistance_broke_two = False

        for x in range(30):

            ticker_contract = Stock(ticker, 'SMART', 'USD')
            [ticker_close] = ib.reqTickers(ticker_contract)

            time.sleep(2)

            if ticker_close.marketPrice() > highest_price:
                highest_price = ticker_close.marketPrice()
                print('Highest Price: ', highest_price)

        while not resistance_broke_two:

            time.sleep(1)

            ticker_contract = Stock(ticker, 'SMART', 'USD')
            [ticker_close] = ib.reqTickers(ticker_contract)

            print('\nChecking for second breakout...')
            print("Resistance Price", highest_price)
            print("Current Price", ticker_close.marketPrice())

            if ticker_close.marketPrice() >= highest_price * 1.005:
                resistance_broke_two = True
                print("\nResistance Two Broke at $" + str(ticker_close.marketPrice()) + "!")

                breakout_price = ticker_close.marketPrice()

                return ticker, breakout_price, resistance_broke_two

    def check_first_breakout(self, ticker, breakout_area, ib):
        ticker_contract = Stock(ticker, 'SMART', 'USD')

        [ticker_close] = ib.reqTickers(ticker_contract)

        breakout_area = round(breakout_area * 1.02, 2)

        limit_market_difference = 100 - self.get_percent(ticker_close.marketPrice(), breakout_area)

        print("Current Price:", ticker_close.marketPrice())
        print("Difference", str(round(abs(limit_market_difference), 2)) + "%")
        print('Checking for first breakout...')

        resistance_broke_one = False

        if ticker_close.marketPrice() > breakout_area:
            resistance_broke_one = True
            print("\nResistance One Broke at $" + str(ticker_close.marketPrice()) + "!")

            resistance = ticker_close.marketPrice()

            return ticker, resistance, resistance_broke_one

        else:
            return ticker, 0, resistance_broke_one

    def buy_stock(self, ticker, breakout_price, ib):

       ticker_contract = Stock(ticker, 'SMART', 'USD')
       [ticker_close] = ib.reqTickers(ticker_contract)

       acc_vals = float([v.value for v in ib.accountValues() if v.tag == 'CashBalance' and v.currency == 'USD'][0])

       percent_of_acct_to_trade = 0.1

       qty = (acc_vals // breakout_price) * percent_of_acct_to_trade
       qty = floor(qty)

       limit_price = round(breakout_price * 1.005, 2)
       take_profit = round(breakout_price * 1.15, 2)
       stop_loss_price = round(breakout_price * 0.985, 2)

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
