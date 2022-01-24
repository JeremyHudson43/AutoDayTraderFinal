from ib_insync.contract import Stock
from ib_insync.ib import IB, ScannerSubscription, TagValue
import pandas as pd
import random
import finviz
import datetime as dt
import traceback
import time

def value_to_float(x):
    if type(x) == float or type(x) == int:
        return x
    if 'K' in x:
        if len(x) > 1:
            return float(x.replace('K', '')) * 1000
        return 1000.0
    if 'M' in x:
        if len(x) > 1:
            return float(x.replace('M', '')) * 1000000
        return 1000000.0
    if 'B' in x:
        if len(x) > 1:
            return float(x.replace('B', '')) * 1000000000
        return 1000000000.0
    if 'T' in x:
        if len(x) > 1:
            return float(x.replace('T', '')) * 1000000000000
        return 1000000000000000.0

    return 0.0

def get_percent(first, second):
    if first == 0 or second == 0:
        return 0
    else:
        percent = first / second * 100
    return percent

def get_AH_gappers():

    ib = IB()

    ib.connect('127.0.0.1', 7497, clientId=random.randint(0, 300))

    topPercentGainerListed= ScannerSubscription(
        instrument='STK',
        locationCode='STK.US.MAJOR',
        scanCode='TOP_PERC_GAIN')

    tagValues = [
        TagValue("changePercAbove", "5"),
        TagValue('priceAbove', 1),
        TagValue('priceBelow', 25),
    ]

    # the tagValues are given as 3rd argument; the 2nd argument must always be an empty list
    # (IB has not documented the 2nd argument and it's not clear what it does)
    scanner = ib.reqScannerData(topPercentGainerListed, [], tagValues)

    symbols = [sd.contractDetails.contract.symbol for sd in scanner]

    date = dt.datetime.now().replace(microsecond=0).date()

    current_time = dt.datetime.now().replace(microsecond=0).time()
    current_time = dt.datetime.combine(date, current_time)

    market_open = "9:30:00"
    market_open = dt.datetime.strptime(market_open, '%H:%M:%S').time()
    market_open = dt.datetime.combine(date, market_open)

    market_close = "16:00:00"
    market_close = dt.datetime.strptime(market_close, '%H:%M:%S').time()
    market_close = dt.datetime.combine(date, market_close)

    after_hours_close = "20:00:00"
    after_hours_close = dt.datetime.strptime(after_hours_close, '%H:%M:%S').time()
    after_hours_close = dt.datetime.combine(date, after_hours_close)

    while current_time < after_hours_close:

        time.sleep(60)

        current_time = dt.datetime.now().replace(microsecond=0).time()
        current_time = dt.datetime.combine(date, current_time)

        # loop through the scanner results and get the contract details of top 20 results
        for stock in symbols[:20]:

            try:

                if current_time > market_close or current_time < market_open:

                    security = Stock(stock, 'SMART', 'USD')
                    [ticker_close] = ib.reqTickers(security)
                    price = ticker_close.marketPrice()

                    finviz_stock = finviz.get_stock(stock)

                    stock_float = value_to_float(finviz_stock['Shs Float'])
                    stock_sector = finviz_stock['Sector']

                    diff = market_close - current_time
                    seconds = round(diff.seconds)

                    # Fetching historical data when market is closed for testing purposes
                    premarket_data = pd.DataFrame(
                        ib.reqHistoricalData(
                            security,
                            endDateTime='',
                            durationStr= str(seconds) + ' S',
                            barSizeSetting='1 min',
                            whatToShow="TRADES",
                            useRTH=False,
                            formatDate=1
                        ))

                    volume = sum(premarket_data['volume'].tolist()) * 100
                    ratio = get_percent(volume, stock_float)

                    if ratio > 0 and stock_float < 30000000:

                        file_to_modify = open("afterhours.txt", "a")

                        print('Ticker', security.symbol)
                        print('Price', price)
                        print("Shares Float", stock_float)
                        print("Volume", volume)
                        print("Stock Sector", stock_sector)
                        print('Afterhours Volume is', ratio, '% of Shares Float')
                        print('Afterhours High is', premarket_data['high'].max())
                        print('Time of access is', current_time)
                        print('')

                        file_to_modify.write('Ticker: ' + security.symbol + '\n')
                        file_to_modify.write('Price: ' + str(price) + '\n')
                        file_to_modify.write('Shares Float: ' + str(stock_float) + '\n')
                        file_to_modify.write('Volume: ' + str(volume) + '\n')
                        file_to_modify.write('Stock Sector: ' + str(stock_sector) + '\n')
                        file_to_modify.write('Afterhours Volume is: ' + str(ratio) + '% of Shares Float\n')
                        file_to_modify.write('Afterhours High is: ' + str(premarket_data['high'].max()) + '\n')
                        file_to_modify.write('Time of access is: ' + str(current_time) + '\n')

            except Exception as err:
                print(traceback.format_exc())


def get_PM_gappers():

    ib = IB()

    ib.connect('127.0.0.1', 7497, clientId=random.randint(0, 300))

    topPercentGainerListed = ScannerSubscription(
        instrument='STK',
        locationCode='STK.US.MAJOR',
        scanCode='TOP_PERC_GAIN')

    tagValues = [
        TagValue("changePercAbove", "5"),
        TagValue('priceAbove', 1),
        TagValue('priceBelow', 25),
    ]

    # the tagValues are given as 3rd argument; the 2nd argument must always be an empty list
    # (IB has not documented the 2nd argument and it's not clear what it does)
    scanner = ib.reqScannerData(topPercentGainerListed, [], tagValues)

    symbols = [sd.contractDetails.contract.symbol for sd in scanner]

    df = pd.DataFrame()

    date = dt.datetime.now().replace(microsecond=0).date()

    current_time = dt.datetime.now().replace(microsecond=0).time()
    current_time = dt.datetime.combine(date, current_time)

    market_open = "9:30:00"
    market_open = dt.datetime.strptime(market_open, '%H:%M:%S').time()
    market_open = dt.datetime.combine(date, market_open)

    market_close = "16:00:00"
    market_close = dt.datetime.strptime(market_close, '%H:%M:%S').time()
    market_close = dt.datetime.combine(date, market_close)

    while current_time < market_open:

        current_time = dt.datetime.now().replace(microsecond=0).time()
        current_time = dt.datetime.combine(date, current_time)

        time.sleep(60)

        # loop through the scanner results and get the contract details of top 20 results
        for stock in symbols[:20]:

            try:

                if current_time > market_close or current_time < market_open:

                    security = Stock(stock, 'SMART', 'USD')
                    [ticker_close] = ib.reqTickers(security)
                    price = ticker_close.marketPrice()

                    finviz_stock = finviz.get_stock(stock)

                    stock_float = value_to_float(finviz_stock['Shs Float'])
                    stock_sector = finviz_stock['Sector']

                    diff = market_open - current_time
                    seconds = round(diff.seconds)

                    # Fetching historical data when market is closed for testing purposes
                    premarket_data = pd.DataFrame(
                        ib.reqHistoricalData(
                            security,
                            endDateTime='',
                            durationStr=str(seconds) + ' S',
                            barSizeSetting='1 min',
                            whatToShow="TRADES",
                            useRTH=False,
                            formatDate=1
                        ))

                    volume = sum(premarket_data['volume'].tolist()) * 100
                    ratio = get_percent(volume, stock_float)

                    if ratio > 0 and stock_float < 30000000:

                        file_to_modify = open("afterhours.txt", "a")

                        print('Ticker', security.symbol)
                        print('Price', price)
                        print("Shares Float", stock_float)
                        print("Volume", volume)
                        print("Stock Sector", stock_sector)
                        print('Premarket Volume is', ratio, '% of Shares Float')
                        print('Premarket High is', premarket_data['high'].max())
                        print('Time of access is', current_time)
                        print('')

                        file_to_modify.write('Ticker: ' + security.symbol + '\n')
                        file_to_modify.write('Price: ' + str(price) + '\n')
                        file_to_modify.write('Shares Float: ' + str(stock_float) + '\n')
                        file_to_modify.write('Volume: ' + str(volume) + '\n')
                        file_to_modify.write('Stock Sector: ' + str(stock_sector) + '\n')
                        file_to_modify.write('Premarket Volume is: ' + str(ratio) + '% of Shares Float\n')
                        file_to_modify.write('Premarket High is: ' + str(premarket_data['high'].max()) + '\n')
                        file_to_modify.write('Time of access is: ' + str(current_time) + '\n')

            except Exception as err:
                print(traceback.format_exc())

    ib.disconnect()

    return df

get_AH_gappers()
time.sleep(3600)
get_PM_gappers()