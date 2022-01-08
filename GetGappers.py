from ib_insync.contract import Stock
from ib_insync.ib import IB, ScannerSubscription, TagValue
import pandas as pd
import random
from bs4 import BeautifulSoup

class GetGapper_Driver():

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
        volume_float_ratios = []
        premarket_highs = []

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

        print(symbols)

        df = pd.DataFrame()

        # loop through the scanner results and get the contract details
        for stock in symbols[:10]:

            try:

                print(stock)

                security = Stock(stock, 'SMART', 'USD')

                # request the fundamentals
                fundamentals = ib.reqFundamentalData(security, 'ReportSnapshot')

                soup = BeautifulSoup(str(fundamentals), 'xml')

                shares = soup.find('SharesOut').text
                shares = float(shares)

                price = float(soup.find('Ratio').text)

                # Fetching historical data when market is closed for testing purposes
                premarket_data = pd.DataFrame(
                    ib.reqHistoricalData(
                        security,
                        endDateTime='09:29:00',
                        durationStr='1 D',
                        barSizeSetting='1 min',
                        whatToShow="TRADES",
                        useRTH=False,
                        formatDate=1
                    ))

                volume = sum(premarket_data['volume'].tolist()) * 100
                ratio = self.get_percent(volume, shares)

                if ratio >= 10 and volume > 150000 and shares < 25000000:
                    print('Ticker', security.symbol)
                    print('Price', price)
                    print("Shares Outstanding", shares)
                    print("Volume", volume)
                    print('Premarket Volume is', ratio, '% of Shares Outstanding\n')
                    print('Premarket High is', ratio)

                    tickers.append(security.symbol)
                    prices.append(price)
                    volumes.append(volume)
                    floats.append(shares)
                    volume_float_ratios.append(ratio)
                    premarket_highs.append(premarket_data['high'].max())

            except Exception as err:
                print(err)

        df['Ticker'] = tickers
        df['Price'] = prices
        df['Volume'] = volumes
        df['Float'] = floats
        df['V/F Ratio'] = volume_float_ratios
        df['Premarket_High'] = premarket_highs

        print(df)

        return df