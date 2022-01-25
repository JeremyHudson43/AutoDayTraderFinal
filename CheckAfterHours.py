from ib_insync.contract import Stock
from ib_insync.ib import IB, ScannerSubscription, TagValue
import random
import datetime as dt
import traceback
import yfinance as yf
import finviz
import time
import pandas as pd

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


def get_PM_gappers():

    ib = IB()
    ib.connect('127.0.0.1', 7497, clientId=random.randint(0, 300))

    date = dt.datetime.now().replace(microsecond=0).date()

    while True:

        current_time = dt.datetime.now().replace(microsecond=0).time()
        current_time = dt.datetime.combine(date, current_time)

        topPercentGainerListed = ScannerSubscription(
            instrument='STK',
            locationCode='STK.US.MAJOR',
            scanCode='TOP_TRADE_RATE')

        tagValues = [
            TagValue("changePercAbove", "5"),
            TagValue('priceAbove', 1),
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
                    # print(symbol)
                    final_symbols.append(symbol)

            except Exception as err:
                print(err)

        # loop through the scanner results and get the contract details of top 20 results
        for stock in final_symbols[:3]:

            print(stock)

            time.sleep(15)

            try:

                ticker = yf.Ticker(stock)

                title = ticker.news[0]['title']

                time_of_news = dt.datetime.fromtimestamp(ticker.news[0]['providerPublishTime'])
                news_datetime = time_of_news.replace(microsecond=0)

                if 300 < (current_time - news_datetime).total_seconds() < 900:

                    security = Stock(stock, 'SMART', 'USD')
                    [ticker_close] = ib.reqTickers(security)
                    price = ticker_close.marketPrice()

                    finviz_stock = finviz.get_stock(stock)
                    finviz_price = finviz_stock['Price']

                    stock_float = value_to_float(finviz_stock['Shs Float'])
                    stock_sector = finviz_stock['Sector']

                    if stock_float < 30000000:

                        change = 100 - get_percent(float(finviz_price), price)
                        change_perc = round(change, 2)

                        # Fetching historical data when market is closed for testing purposes
                        afterhours_data = pd.DataFrame(
                            ib.reqHistoricalData(
                                security,
                                endDateTime='',
                                durationStr= '120 S',
                                barSizeSetting='1 min',
                                whatToShow="TRADES",
                                useRTH=False,
                                formatDate=1
                            ))

                        volume = sum(afterhours_data['volume'].tolist()) * 100

                        if 1 <= change_perc <= 10 and volume > 5000:

                            today = dt.datetime.today().strftime('%Y-%m-%d')

                            filepath = 'C:\\Users\\Frank Einstein\\PycharmProjects\\AutoDaytrader\\news\\' + today + '_news.txt'
                            file_to_modify = open(filepath, "a+")
                            file_to_modify.close()

                            with open(filepath) as myfile:
                                if 'Ticker: ' + security.symbol not in myfile.read():

                                    myfile.close()

                                    print('Ticker', security.symbol)
                                    print('Current Price', price)
                                    print('Close Price', finviz_price)
                                    print("Shares Float", stock_float)
                                    print("120 second volume", volume)
                                    print("Stock Sector", stock_sector)
                                    print('Time of access is', current_time)
                                    print('Change Perc ', str(change_perc) + "%")
                                    print('Time of News', news_datetime)
                                    print('Title:', title)
                                    print('')

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
                                    file_to_modify.write('Time of News: ' + str(news_datetime) + '\n')
                                    file_to_modify.write('Title: ' + title + '\n')
                                    file_to_modify.write('\n')

                                    file_to_modify.close()

            except Exception as err:
                print(traceback.format_exc())

    ib.disconnect()

get_PM_gappers()
