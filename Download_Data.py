from ib_insync.contract import Stock
from ib_insync.ib import IB
import pandas as pd
import random
from finviz.screener import Screener
import time
import os
from os.path import exists

# filters = ['sh_float_u20']
# stock_list = Screener(filters=filters, table='Performance', order='price')

ib = IB()

ib.connect('127.0.0.1', 7497, clientId=random.randint(0, 300))

directory = 'C:\\Users\\Frank Einstein\\PycharmProjects\\AutoDaytrader\\small_cap_records_days'

df = pd.read_csv('test_all.csv')
df = df.sort_values(by=['stock'])

stock_list = df['stock'].to_list()
date_list = df['date'].to_list()

for ticker, date in zip(stock_list, date_list):

    csv_path = 'small_cap_records_days\\' + ticker + '.csv'

    if exists(csv_path):

        if date not in [x.split(' ')[0] for x in pd.read_csv(csv_path)['date'].to_list()]:

            stock = ticker

            print(stock)

            security = Stock(stock, 'SMART', 'USD')

            market_date = date.replace('-', '') + ' 16:00:00'

            # Fetching historical data when market is closed for testing purposes
            market_data = pd.DataFrame(
                ib.reqHistoricalData(
                    security,
                    endDateTime=market_date,
                    durationStr='2 D',
                    barSizeSetting='1 min',
                    whatToShow="TRADES",
                    useRTH=False,
                    formatDate=1,
                    timeout = 0
                ))

            pd.read_csv(csv_path).append(market_data).to_csv(csv_path, index=False)
            print(date not in [x.split(' ')[0] for x in pd.read_csv(csv_path)['date'].to_list()])

    elif not exists(csv_path):
        stock = ticker

        security = Stock(stock, 'SMART', 'USD')

        market_date = date.replace('-', '') + ' 16:00:00'

        # Fetching historical data when market is closed for testing purposes
        market_data = pd.DataFrame(
            ib.reqHistoricalData(
                security,
                endDateTime=market_date,
                durationStr='2 D',
                barSizeSetting='1 min',
                whatToShow="TRADES",
                useRTH=False,
                formatDate=1,
                timeout=0
            ))

        market_data.to_csv(csv_path)