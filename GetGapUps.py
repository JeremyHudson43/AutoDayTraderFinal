from ib_insync.contract import Stock
from ib_insync.ib import IB, ScannerSubscription, TagValue
import pandas as pd
import random
from bs4 import BeautifulSoup
import finviz

class GetGapper_Driver():

    def value_to_float(self, x):
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

    def get_percent(self, first, second):
        if first == 0 or second == 0:
            return 0
        else:
            percent = first / second * 100
        return percent

    def get_gappers(self):

        tickers = []
        prices = []
        volumes = []
        floats = []
        volume_float_ratio = []
        premarket_highs = []
        sectors = []

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

        df = pd.DataFrame()

        # loop through the scanner results and get the contract details of top 20 results
        for stock in symbols[:10]:

            try:

                security = Stock(stock, 'SMART', 'USD')

                finviz_stock = finviz.get_stock(stock)

                stock_float = self.value_to_float(finviz_stock['Shs Float'])
                stock_sector = finviz_stock['Sector']

                # request the fundamentals
                fundamentals = ib.reqFundamentalData(security, 'ReportSnapshot')

                soup = BeautifulSoup(str(fundamentals), 'xml')

                price = float(soup.find('Ratio').text)

                # Fetching historical data when market is closed for testing purposes
                premarket_data = pd.DataFrame(
                    ib.reqHistoricalData(
                        security,
                        endDateTime='09:29:59',
                        durationStr='1 D',
                        barSizeSetting='1 min',
                        whatToShow="TRADES",
                        useRTH=False,
                        formatDate=1
                    ))

                volume = sum(premarket_data['volume'].tolist()) * 100
                ratio = self.get_percent(volume, stock_float)

                # if ratio >= 5 and volume > 150000 and stock_float < 30000000:
                print('Ticker', security.symbol)
                print('Price', price)
                print("Shares Float", stock_float)
                print("Volume", volume)
                print("Stock Sector", stock_sector )
                print('Premarket Volume is', ratio, '% of Shares Float\n')
                print('Premarket High is', premarket_data['high'].max())

                tickers.append(security.symbol)
                prices.append(price)
                volumes.append(volume)
                floats.append(stock_float)
                volume_float_ratio.append(ratio)
                premarket_highs.append(premarket_data['high'].max())
                sectors.append(stock_sector)

            except Exception as err:
                print(err)

        ib.disconnect()

        df['Ticker'] = tickers
        df['Price'] = prices
        df['Volume'] = volumes
        df['Shares Float'] = floats
        df['V/F Ratio'] = volume_float_ratio
        df['Premarket High'] = premarket_highs
        df['Sector'] = sectors

        return df