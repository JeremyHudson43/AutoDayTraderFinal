from ib_insync.contract import Stock
from ib_insync.ib import IB, ScannerSubscription, TagValue, LimitOrder, Order
import random
import datetime as dt
import traceback
import yfinance as yf
import finviz
import time
import pandas as pd
from datetime import timedelta
from math import floor
import sys


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


def get_news(stock, current_time):

    ticker = yf.Ticker(stock)

    title = ticker.news[0]['title']

    if len(title) > 0:

        time_of_news = dt.datetime.fromtimestamp(ticker.news[0]['providerPublishTime'])
        news_datetime = time_of_news.replace(microsecond=0)

        time_elapsed = (current_time - news_datetime).total_seconds()

        return title, time_elapsed

    return '', 0


def buy_stock(ticker, ib, limit_price):

   ticker_contract = Stock(ticker, 'SMART', 'USD')

   acc_vals = float([v.value for v in ib.accountValues() if v.tag == 'CashBalance' and v.currency == 'USD'][0])

   percent_of_acct_to_trade = 0.03

   qty = (acc_vals // limit_price) * percent_of_acct_to_trade
   qty = floor(qty)

   buy_order = LimitOrder(orderId=5, action='BUY', totalQuantity=qty, lmtPrice=limit_price)
   buy_order.outsideRth = True

   ib.placeOrder(ticker_contract, buy_order)

   time.sleep(30)

   sell_order = Order(orderId=6, orderType = 'MKT', action='SELL', totalQuantity=qty)
   ib.placeOrder(ticker_contract, sell_order)


def get_pm_gappers():

    ib = IB()
    ib.connect('127.0.0.1', 7497, clientId=random.randint(0, 300))

    date = dt.datetime.now().replace(microsecond=0).date()

    while True:

        topPercentGainerListed = ScannerSubscription(
            instrument='STK',
            locationCode='STK.US.MAJOR',
            scanCode='TOP_TRADE_RATE')

        tagValues = [
            TagValue("changePercAbove", "5"),
            TagValue('priceBelow', 25),
        ]

        # the tagValues are given as 3rd argument; the 2nd argument must always be an empty list
        # (IB has not documented the 2nd argument and it's not clear what it does)
        scanner = ib.reqScannerData(topPercentGainerListed, [], tagValues)

        symbols = [sd.contractDetails.contract.symbol for sd in scanner]

        final_symbols = []

        for symbol in symbols:
            try:

                stock_to_remove = finviz.get_stock(symbol)
                company = stock_to_remove['Company']

                if company != 'Financial':
                    final_symbols.append(symbol)

            except Exception as err:
                print(err)

        # loop through the scanner results and get the contract details of top 20 results
        for stock in final_symbols[:5]:

            current_time = dt.datetime.now().replace(microsecond=0).time()
            current_time = dt.datetime.combine(date, current_time)

            try:

                security = Stock(stock, 'SMART', 'USD')
                [ticker_close] = ib.reqTickers(security)
                price = ticker_close.marketPrice()

                finviz_stock = finviz.get_stock(stock)
                finviz_price = finviz_stock['Price']

                stock_float = value_to_float(finviz_stock['Shs Float'])
                stock_sector = finviz_stock['Sector']

                if stock_float < 10000000 and float(finviz_price) < 10:

                    change = 100 - get_percent(float(finviz_price), price)
                    change_perc = round(change, 2)

                    AH_open = "4:00:00 PM"

                    AH_open = dt.datetime.strptime(AH_open, '%I:%M:%S %p').time()
                    AH_open = dt.datetime.combine(date, AH_open)

                    diff = str(int((current_time - AH_open).total_seconds()))

                    # Fetching historical data when market is closed for testing purposes
                    afterhours_data = pd.DataFrame(
                        ib.reqHistoricalData(
                            security,
                            endDateTime='',
                            durationStr=diff + ' S',
                            barSizeSetting='1 min',
                            whatToShow="TRADES",
                            useRTH=False,
                            formatDate=1
                        ))

                    volume = sum(afterhours_data['volume'].tolist()) * 100

                    print("Volume", volume)
                    print("Change", change_perc)

                    if 10 <= change_perc <= 40 and 50000 < volume < 1000000:

                        title, time_elapsed = get_news(stock, current_time)

                        if 0 < time_elapsed < 1200:

                            print(title)

                            print('Ticker', security.symbol)
                            print('Current Price', price)
                            print('Close Price', finviz_price)
                            print("Shares Float", stock_float)
                            print("120 second volume", volume)
                            print("Stock Sector", stock_sector)
                            print('Time of access is', current_time)
                            print('Change Perc ', str(change_perc) + "%")
                            # print('Time of News', news_datetime)
                            # print('Title:', title)
                            print('')

                            today = dt.datetime.today().strftime('%Y-%m-%d')
                            filepath = 'C:\\Users\\Frank Einstein\\PycharmProjects\\AutoDaytrader\\Data\\news\\' + today + '_news.txt'

                            file_to_modify = open(filepath, "a+")

                            file_to_modify.write('\n')
                            file_to_modify.write('Ticker: ' + security.symbol + '\n')
                            file_to_modify.write('Current Price: ' + str(price) + '\n')
                            file_to_modify.write('Close Price: ' + str(finviz_price) + '\n')
                            file_to_modify.write('Shares Float: ' + str(stock_float) + '\n')
                            file_to_modify.write('120 second volume: ' + str(volume) + '\n')
                            file_to_modify.write('Stock Sector: ' + str(stock_sector) + '\n')
                            file_to_modify.write('Time of access is: ' + str(current_time) + '\n')
                            file_to_modify.write('Change Perc ' + str(change_perc) + "%\n")
                            # file_to_modify.write('Time of News: ' + str(news_datetime) + '\n')
                            # file_to_modify.write('Title: ' + title + '\n')
                            file_to_modify.write('\n')

                            file_to_modify.close()

                            buy_stock(stock, ib, price)

                            sys.exit(0)

                time.sleep(30)

            except Exception as err:
                print(traceback.format_exc())

    ib.disconnect()


date = dt.datetime.now().replace(microsecond=0).date()

current_time = dt.datetime.now().replace(microsecond=0).time()
current_time = dt.datetime.combine(date, current_time)

PM_open = "4:00:00 AM"

PM_open = dt.datetime.strptime(PM_open, '%I:%M:%S %p').time()
PM_open = dt.datetime.combine(date, PM_open) + timedelta(days=1)

diff = abs((PM_open - current_time).total_seconds())

# print("Sleeping for " + str(diff) + " seconds")

# time.sleep(diff)

get_pm_gappers()
