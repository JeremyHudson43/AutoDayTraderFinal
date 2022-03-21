from ib_insync import *
import random
from datetime import *
import time
import pandas as pd
from dateutil import parser
import sys
import talib
import math

ib = IB()
ib.connect('127.0.0.1', 7497, clientId=random.randint(0, 300))


def get_wr(high, low, close, lookback):
    highh = high.rolling(lookback).max()
    lowl = low.rolling(lookback).min()
    wr = 100 * ((close - highh) / (highh - lowl))
    return wr

def check_time():
    # check if it is before 2:30 PM
    if datetime.now().hour == 14 and datetime.now().minute > 30:
        return True
    else:
        return False

def sleep_until_market_open():
    now = datetime.now()  # time object

    StartTime = pd.to_datetime("9:40").tz_localize('America/New_York')
    TimeNow = pd.to_datetime(now).tz_localize('America/New_York')

    if StartTime > TimeNow:
        time_until_market_open = (StartTime - TimeNow).total_seconds()
        time.sleep(time_until_market_open)


def sell_stock(ib, contract, orders):

   for order in orders:
       try:
        ib.cancelOrder(order)
       except Exception as e:
           print(e)

   option = [v for v in ib.positions() if v.contract.secType == 'OPT' and v.contract.symbol == 'SPY'][0]
   qty = option.position

   if qty > 0:

       contract_data = ib.reqTickers(*[contract])[0]
       lmt_price = (contract_data.bid + contract_data.ask) / 2

       order = Order(orderId=270, action='Sell', orderType='LMT', lmtPrice=lmt_price, totalQuantity=qty)

       ib.placeOrder(contract, order)

       print('\nSold ' + str(contract.symbol) + " at the end of the day!")

       time.sleep(10)

       sys.exit(0)


def place_order():

    orders = []

    extreme_value = False

    while not extreme_value:

        past_two_thirty = check_time()

        if not past_two_thirty:

            ticker = 'SPY'

            put_year = '2022'
            put_month = '03'
            put_day = '18'

            call_year = '2022'
            call_month = '03'
            call_day = '18'

            ticker_contract = Stock('SPY', 'SMART', 'USD')

            if not extreme_value:
                timeToSleep = (5*60 - time.time() % (5*60))

                print("Sleeping for " + str(timeToSleep) + " seconds")
                time.sleep(timeToSleep)

            market_data = pd.DataFrame(
                ib.reqHistoricalData(
                    ticker_contract,
                    endDateTime='',
                    durationStr='7 D',
                    barSizeSetting='5 mins',
                    whatToShow="TRADES",
                    formatDate=1,
                    useRTH=True,
                    timeout=0
                ))

            two_hundred_ema = talib.EMA(market_data['close'].values, timeperiod=200)[-1]
            twenty_five_ema = talib.EMA(market_data['close'].values, timeperiod=25)[-1]
            five_ema = talib.EMA(market_data['close'].values, timeperiod=5)[-1]
            ten_ema = talib.EMA(market_data['close'].values, timeperiod=10)[-1]

            last_close = market_data['close'].iloc[-1]

            williams_perc = get_wr(market_data['high'], market_data['low'], market_data['close'], 2).iloc[-1]

            market_data['williams_perc'] = get_wr(market_data['high'], market_data['low'], market_data['close'], 2)

            market_data.to_csv('C:\\Users\\Frank Einstein\\Desktop\\results\\market_data.csv')

            print("\nLast Close: " + str(last_close) + '\n')
            print("Williams %: " + str(williams_perc) + '\n')
            print('200 SMA: ' + str(two_hundred_ema) + '\n')
            print('25 EMA: ' + str(twenty_five_ema) + '\n')
            print('10 EMA: ' + str(ten_ema) + '\n')
            print('5 EMA: ' + str(five_ema) + '\n')

            print('- - - - - - - - - - - - - - - - - - - - \n')

            if williams_perc <= -85 and last_close > two_hundred_ema and last_close > twenty_five_ema and five_ema > ten_ema

                [SPY_close] = ib.reqTickers(ticker_contract)
                Current_SPY_Value = SPY_close.marketPrice()

                extreme_value = True

                call_strike = math.ceil(Current_SPY_Value)
                call = Option(ticker, call_year + call_month + call_day, call_strike, 'C', "SMART")

                contract = call

            elif williams_perc >= -15 and last_close < two_hundred_ema and last_close < twenty_five_ema and five_ema < ten_ema:

                [SPY_close] = ib.reqTickers(ticker_contract)
                Current_SPY_Value = SPY_close.marketPrice()

                extreme_value = True

                put_strike = math.floor(Current_SPY_Value)
                put = Option(ticker, put_year + put_month + put_day, put_strike, 'P', "SMART")

                contract = put

            else:
                print("Waiting for extreme value...\n")

        acc_vals = float([v.value for v in ib.accountValues() if v.tag == 'CashBalance' and v.currency == 'USD'][0])

        ib.qualifyContracts(contract)
        contract_data = ib.reqTickers(*[contract])[0]

        bid = contract_data.bid
        ask = contract_data.ask
        delta = abs(contract_data.bidGreeks.delta)

        mid = (bid + ask) / 2

        qty = (acc_vals // mid) - 1

        limit_price = mid
        take_profit = mid + (delta * 0.2)
        stop_loss_price = mid - delta

        limit_price = round(limit_price, 2)
        take_profit = round(take_profit, 2)
        stop_loss_price = round(stop_loss_price, 2)

        buy_order = ib.bracketOrder(
                   'BUY',
                   quantity=qty,
                   limitPrice=limit_price,
                   takeProfitPrice=take_profit,
                   stopLossPrice=stop_loss_price
               )

        for o in buy_order:
           o.tif = 'GTC'
           ib.sleep(0.00001)
           ib.placeOrder(contract, o)
           orders.append(o)

    return extreme_value, contract, orders


sleep_until_market_open()


extreme_value, contract, orders = place_order()

if extreme_value:
    timeToSleep = 300
    print("Sleeping for " + str(timeToSleep) + " seconds")

    time.sleep(timeToSleep)
    sell_stock(ib, contract, orders)
