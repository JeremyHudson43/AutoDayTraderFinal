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

       ticker_contract = Stock(ticker, 'SMART', 'USD')

       order = Order(orderId=15, action='Sell', orderType='MKT', totalQuantity=qty)

       ib.placeOrder(ticker_contract, order)

       print('Sold ' + str(ticker) +  "!")

       time.sleep(10)

    def buy_stock(self, ticker, premarket_high, multiplier, ib):

       order_list = []

       ticker_contract = Stock(ticker, 'SMART', 'USD')

       [ticker_close] = ib.reqTickers(ticker_contract)

       if premarket_high < ticker_close.marketPrice() * 1.09:

           acc_vals = float([v.value for v in ib.accountValues() if v.tag == 'CashBalance' and v.currency == 'USD'][0])

           limit_price = float(str(round(premarket_high * 1.005, 2)))
           take_profit = float(str(round(premarket_high * 1.105, 2)))
           stop_loss_price = float(str(round(premarket_high * 0.985, 2)))

           percent_of_acct_to_trade = 0.05

           qty = (acc_vals // limit_price) * percent_of_acct_to_trade
           qty = round(qty)

           pct_difference = round(self.get_percent((qty * limit_price), acc_vals), 2)

           print(100 - self.get_percent(ticker_close.marketPrice(), limit_price))

           if 100 - self.get_percent(ticker_close.marketPrice(), limit_price) < 1:

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

                   o.orderId = o.orderId * multiplier

                   if o.action == 'SELL':
                       o.parentId = o.parentId * multiplier

                   if o.action == 'BUY':
                      order_list.append(o)

                   ib.placeOrder(ticker_contract, o)

               return order_list

       else:
        return None
