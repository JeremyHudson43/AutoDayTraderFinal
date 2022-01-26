import time
from ib_insync.contract import Stock
from ib_insync.ib import IB
from datetime import datetime
from ib_insync import Order
import pandas as pd
import random
import sys
from math import floor

# Logging into Interactive Broker TWS
ib = IB()

# port for IB gateway : 4002
# port for IB TWS : 7497
ib.connect('127.0.0.1', 7497, clientId=random.randint(0, 300))

# To get the current market value, first create a contract for the underlyer,
# we are selecting Tesla for now with SMART exchanges:
SPY = Stock('SPY', 'SMART', 'USD')

# Fetching historical data when market is closed for testing purposes
market_data = pd.DataFrame(
    ib.reqHistoricalData(
        SPY,
        endDateTime='',
        durationStr='1 D',
        barSizeSetting='1 min',
        whatToShow="TRADES",
        useRTH=False,
        formatDate=1,
        keepUpToDate=True
    ))

start = datetime.strptime('04:00:00', '%H:%M:%S').time()
end = datetime.strptime('09:29:59', '%H:%M:%S').time()

premarket_data = market_data[market_data['date'].dt.time.between(start, end)]

high_value = max(premarket_data['high'].to_list())
low_value = min(premarket_data['low'].to_list())

ib.disconnect()


def set_trailing_stop(stock, time_until_market_close, qty):

    ib.disconnect()

    ib.connect('127.0.0.1', 7497, clientId=random.randint(0, 300))

    time.sleep(20)

    stock = Stock(stock, 'SMART', 'USD')

    print('Bought ' + stock.symbol + "! " + 'Sleeping until 15 minutes before market close')

    sell_order = Order(orderId=random.randint(301, 600), action='Sell', orderType='TRAIL',
                       trailingPercent=1, totalQuantity=qty)

    ib.placeOrder(stock, sell_order)

    time.sleep(time_until_market_close - 600)

    ib.reqGlobalCancel()

    qty_owned = ib.positions()[0].position

    sell_stock(ib, qty_owned, stock.symbol)

    ib.disconnect()


def sell_stock(ib, qty, ticker):
    ib.disconnect()

    ib.connect('127.0.0.1', 7497, clientId=random.randint(900, 1200))

    if qty > 0:
        ticker_contract = Stock(ticker, 'SMART', 'USD')

        order = Order(orderId=27, action='Sell', orderType='MKT', totalQuantity=qty)

        ib.placeOrder(ticker_contract, order)

        print('\nSold ' + str(ticker) + " at the end of the day!")

        time.sleep(10)

        sys.exit(0)

    ib.disconnect()


def check_time():
    ## STARTING THE ALGORITHM ##
    # Time frame: 6.30 hrs

    now = datetime.now() # time object

    StartTime = pd.to_datetime("9:30").tz_localize('America/New_York')
    TimeNow = pd.to_datetime(now).tz_localize('America/New_York')
    EndTime = pd.to_datetime("16:00").tz_localize('America/New_York')

    time_until_market_close = (EndTime - TimeNow).total_seconds()

    # Waiting for Market to Open
    if StartTime > TimeNow:
        wait = (StartTime - TimeNow).total_seconds()
        print("Waiting for Market to Open..")
        print(f"Sleeping for {wait} seconds")
        time.sleep(wait)

    return time_until_market_close


def driver_func():
    ib.connect('127.0.0.1', 7497, clientId=random.randint(0, 300))

    purchased = False

    time_until_market_close = check_time()

    # Run the algorithm till the daily time frame exhausts:
    while time_until_market_close > 900:

        time.sleep(5)

        time_until_market_close = check_time()

        try:
            print("\nLooking for an opportunity!\n")

            [SPY_close] = ib.reqTickers(SPY)

            Current_SPY_Value = SPY_close.marketPrice()

            print('SPY Premarket Low', low_value)
            print('SPY Premarket High', high_value)
            print('SPY Current Value', Current_SPY_Value)

            if Current_SPY_Value > high_value and purchased == False:

                UPRO = Stock('UPRO', 'SMART', 'USD')

                [UPRO_close] = ib.reqTickers(UPRO)

                Current_UPRO_Value = UPRO_close.marketPrice()

                acc_vals = float(
                    [v.value for v in ib.accountValues() if v.tag == 'CashBalance' and v.currency == 'USD'][0])

                percent_of_acct_to_trade = 0.2

                qty = (acc_vals // Current_UPRO_Value) * percent_of_acct_to_trade
                qty = floor(qty)

                buy_order = Order(orderId=random.randint(0, 300), action='Buy', orderType='LIMIT', lmtPrice=Current_UPRO_Value,
                              totalQuantity=qty)

                ib.placeOrder(UPRO, buy_order)

                set_trailing_stop('UPRO', time_until_market_close, qty)

            elif Current_SPY_Value < low_value and purchased == False:

                SPXU = Stock('SPXU', 'SMART', 'USD')

                [SPXU_close] = ib.reqTickers(SPXU)

                Current_SPXU_Value = round(SPXU_close.marketPrice(), 2)

                acc_vals = float(
                    [v.value for v in ib.accountValues() if v.tag == 'CashBalance' and v.currency == 'USD'][0])

                percent_of_acct_to_trade = 0.2

                qty = (acc_vals // Current_SPXU_Value) * percent_of_acct_to_trade
                qty = floor(qty)

                buy_order = Order(orderId=4, action='Buy', orderType='LIMIT', lmtPrice=Current_SPXU_Value,
                              totalQuantity=qty)

                ib.placeOrder(SPXU, buy_order)

                set_trailing_stop('SPXU', time_until_market_close, qty)

        except Exception as err:
            print(err)

    ib.disconnect()

driver_func()import time
from ib_insync.contract import Stock
from ib_insync.ib import IB
from datetime import datetime
from ib_insync import Order
import pandas as pd
import random
import sys
from math import floor

# Logging into Interactive Broker TWS
ib = IB()

# port for IB gateway : 4002
# port for IB TWS : 7497
ib.connect('127.0.0.1', 7497, clientId=random.randint(0, 300))

# To get the current market value, first create a contract for the underlyer,
# we are selecting Tesla for now with SMART exchanges:
SPY = Stock('SPY', 'SMART', 'USD')

# Fetching historical data when market is closed for testing purposes
market_data = pd.DataFrame(
    ib.reqHistoricalData(
        SPY,
        endDateTime='',
        durationStr='1 D',
        barSizeSetting='1 min',
        whatToShow="TRADES",
        useRTH=False,
        formatDate=1,
        keepUpToDate=True
    ))

start = datetime.strptime('04:00:00', '%H:%M:%S').time()
end = datetime.strptime('09:29:59', '%H:%M:%S').time()

premarket_data = market_data[market_data['date'].dt.time.between(start, end)]

high_value = max(premarket_data['high'].to_list())
low_value = min(premarket_data['low'].to_list())

ib.disconnect()


def set_trailing_stop(stock, time_until_market_close, qty):

    ib.disconnect()

    ib.connect('127.0.0.1', 7497, clientId=random.randint(0, 300))

    time.sleep(20)

    stock = Stock(stock, 'SMART', 'USD')

    print('Bought ' + stock.symbol + "! " + 'Sleeping until 15 minutes before market close')

    sell_order = Order(orderId=random.randint(301, 600), action='Sell', orderType='TRAIL',
                       trailingPercent=1, totalQuantity=qty)

    ib.placeOrder(stock, sell_order)

    time.sleep(time_until_market_close - 600)

    ib.reqGlobalCancel()

    qty_owned = ib.positions()[0].position

    sell_stock(ib, qty_owned, stock.symbol)

    ib.disconnect()


def sell_stock(ib, qty, ticker):
    ib.disconnect()

    ib.connect('127.0.0.1', 7497, clientId=random.randint(900, 1200))

    if qty > 0:
        ticker_contract = Stock(ticker, 'SMART', 'USD')

        order = Order(orderId=27, action='Sell', orderType='MKT', totalQuantity=qty)

        ib.placeOrder(ticker_contract, order)

        print('\nSold ' + str(ticker) + " at the end of the day!")

        time.sleep(10)

        sys.exit(0)

    ib.disconnect()


def check_time():
    ## STARTING THE ALGORITHM ##
    # Time frame: 6.30 hrs

    now = datetime.now() # time object

    StartTime = pd.to_datetime("9:30").tz_localize('America/New_York')
    TimeNow = pd.to_datetime(now).tz_localize('America/New_York')
    EndTime = pd.to_datetime("16:00").tz_localize('America/New_York')

    time_until_market_close = (EndTime - TimeNow).total_seconds()

    # Waiting for Market to Open
    if StartTime > TimeNow:
        wait = (StartTime - TimeNow).total_seconds()
        print("Waiting for Market to Open..")
        print(f"Sleeping for {wait} seconds")
        time.sleep(wait)

    return time_until_market_close


def driver_func():
    ib.connect('127.0.0.1', 7497, clientId=random.randint(0, 300))

    purchased = False

    time_until_market_close = check_time()

    # Run the algorithm till the daily time frame exhausts:
    while time_until_market_close > 900:

        time.sleep(5)

        time_until_market_close = check_time()

        try:
            print("\nLooking for an opportunity!\n")

            [SPY_close] = ib.reqTickers(SPY)

            Current_SPY_Value = SPY_close.marketPrice()

            print('SPY Premarket Low', low_value)
            print('SPY Premarket High', high_value)
            print('SPY Current Value', Current_SPY_Value)

            if Current_SPY_Value > high_value and purchased == False:

                UPRO = Stock('UPRO', 'SMART', 'USD')

                [UPRO_close] = ib.reqTickers(UPRO)

                Current_UPRO_Value = UPRO_close.marketPrice()

                acc_vals = float(
                    [v.value for v in ib.accountValues() if v.tag == 'CashBalance' and v.currency == 'USD'][0])

                percent_of_acct_to_trade = 0.2

                qty = (acc_vals // Current_UPRO_Value) * percent_of_acct_to_trade
                qty = floor(qty)

                buy_order = Order(orderId=random.randint(0, 300), action='Buy', orderType='LIMIT', lmtPrice=Current_UPRO_Value,
                              totalQuantity=qty)

                ib.placeOrder(UPRO, buy_order)

                set_trailing_stop('UPRO', time_until_market_close, qty)

            elif Current_SPY_Value < low_value and purchased == False:

                SPXU = Stock('SPXU', 'SMART', 'USD')

                [SPXU_close] = ib.reqTickers(SPXU)

                Current_SPXU_Value = round(SPXU_close.marketPrice(), 2)

                acc_vals = float(
                    [v.value for v in ib.accountValues() if v.tag == 'CashBalance' and v.currency == 'USD'][0])

                percent_of_acct_to_trade = 0.2

                qty = (acc_vals // Current_SPXU_Value) * percent_of_acct_to_trade
                qty = floor(qty)

                buy_order = Order(orderId=4, action='Buy', orderType='LIMIT', lmtPrice=Current_SPXU_Value,
                              totalQuantity=qty)

                ib.placeOrder(SPXU, buy_order)

                set_trailing_stop('SPXU', time_until_market_close, qty)

        except Exception as err:
            print(err)

    ib.disconnect()

driver_func()
