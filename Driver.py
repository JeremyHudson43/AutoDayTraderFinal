import SimpleGapUpScalper
import GetGapUps
import pandas as pd
import time
from datetime import datetime
import traceback
import sys
from ib_insync.ib import IB
import random

scalper = SimpleGapUpScalper.GapUpScalper_Driver()
get_gappers_class = GetGapUps.GetGapper_Driver()

# Logging into Interactive Broker TWS
ib = IB()
ib.connect('127.0.0.1', 7497, clientId=random.randint(0, 300))

def check_time():
    ## STARTING THE ALGORITHM ##
    # Time frame: 6.30 hrs

    now = str(datetime.now().time())  # time object

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

    return StartTime, TimeNow, EndTime, time_until_market_close


def generate_gapper_CSV():

    today = datetime.today().strftime('%Y-%m-%d')

    filepath = 'C:\\Users\\Frank Einstein\\PycharmProjects\\AutoDaytrader\\gapper_records\\gappers_' + today + '.csv'

    df = get_gappers_class.get_gappers()
    df.to_csv(filepath)

    return df


if __name__ == "__main__":

    check_time()

    df = generate_gapper_CSV()

    tickers = df['Ticker'].to_list()
    premarket_highs = df['Premarket High'].to_list()

    purchased = False

    start_time, time_now, end_time, time_until_market_close = check_time()

    while time_now < end_time:
        start_time, time_now, end_time, time_until_market_close = check_time()

        multiplier = 0

        for ticker, premarket_high in zip(tickers, premarket_highs):

            print('- - - - - - - - - ')
            print("Ticker", ticker)
            print("\nPremarket High", premarket_high)

            multiplier = multiplier + 1

            if not purchased:
                purchased, qty, ticker = scalper.buy_stock(ticker, premarket_high, multiplier, ib, purchased)
            elif purchased:

                print('Purchased! Sleeping until 5 minutes before market close')

                time.sleep(time_until_market_close - 300)
                scalper.sell_stock(ib, qty, ticker)

        time.sleep(5)

    sys.exit(0)
