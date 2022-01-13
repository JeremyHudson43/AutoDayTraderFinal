from ib_insync.contract import Stock
from ib_insync.ib import IB
import pandas as pd
import random
from finviz.screener import Screener
import time

filters = ['sh_float_u20']
stock_list = Screener(filters=filters, table='Performance', order='price')

ib = IB()

ib.connect('127.0.0.1', 7497, clientId=random.randint(0, 300))

for ticker in stock_list:

    ticker = ticker['Ticker']

    stock = ticker

    security = Stock(stock, 'SMART', 'USD')

    year = '2021'
    month = '12'
    day = '31'

    market_date = year + month + day + ' 16:00:00'

    # Fetching historical data when market is closed for testing purposes
    market_data = pd.DataFrame(
        ib.reqHistoricalData(
            security,
            endDateTime=market_date,
            durationStr='12 M',
            barSizeSetting='15 mins',
            whatToShow="TRADES",
            useRTH=False,
            formatDate=1
        ))

    if not market_data.empty:
        market_data.to_csv('small_cap_records\\' + ticker  + '.csv')

    time.sleep(5)
