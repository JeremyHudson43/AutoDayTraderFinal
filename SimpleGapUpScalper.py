import time
from ib_insync.contract import Stock
from ib_insync import Order


class GapUpScalper_Driver():

    def get_percent(self, first, second):
        if first == 0 or second == 0:
            return 0
        else:
            percent = first / second * 100
        return percent

    def sell_stock(self, ib):

       ticker = ib.positions()[0]
       qty = [v.position for v in ib.positions()][0]
       
       if qty > 0:
           ticker_contract = Stock(ticker, 'SMART', 'USD')

           order = Order(orderId=30, action='Sell', orderType='MKT', totalQuantity=qty)

           ib.placeOrder(ticker_contract, order)

           print('Sold ' + str(ticker) +  "!")

           time.sleep(10)

    def buy_stock(self, ticker, premarket_high, multiplier, ib):

       ticker_contract = Stock(ticker, 'SMART', 'USD')

       [ticker_close] = ib.reqTickers(ticker_contract)

       if premarket_high * 1.005 < ticker_close.marketPrice() * 1.095:

           acc_vals = float([v.value for v in ib.accountValues() if v.tag == 'CashBalance' and v.currency == 'USD'][0])

           limit_price = float(str(round(premarket_high * 1.005, 2)))

           percent_of_acct_to_trade = 0.05

           qty = (acc_vals // limit_price) * percent_of_acct_to_trade
           qty = round(qty)

           pct_difference = round(self.get_percent((qty * limit_price), acc_vals), 2)

           print(100 - self.get_percent(ticker_close.marketPrice(), limit_price))

           if 100 - self.get_percent(ticker_close.marketPrice(), limit_price) < 0.2:

               print('\nYou bought ' + str(qty) + ' shares of ' + str(ticker) +
                     ' for a total of $' + str(round(qty * limit_price)) + ' USD' +
                     ' which is ' + str(pct_difference) + '% of your account ')

               buy_order = Order(orderId=15 * multiplier, action='BUY', orderType='LMT', totalQuantity=qty, lmtPrice=limit_price)

               ib.placeOrder(ticker_contract, buy_order)

               while not buy_order.isDone():
                   time.sleep(1)

               sell_order = Order(orderId=5 * multiplier, action='Sell', orderType='TRAIL',
                             trailingPercent=2, totalQuantity=qty)

               ib.placeOrder(ticker_contract, sell_order)
