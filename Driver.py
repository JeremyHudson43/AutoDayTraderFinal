import SimpleGapUpScalper
import GetGapUps
import pandas as pd
import multiprocessing
import time
from datetime import datetime
import gc
import traceback
import sys
from ib_insync.ib import IB

scalper = SimpleGapUpScalper.GapUpScalper_Driver()
get_gappers_class = GetGapUps.GetGapper_Driver()


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


def sell_stock(ticker, qty):
    try:
        # sell if you've bought already and haven't sold 5 minutes before close
        scalper.sell_stock(ticker, qty)
        sys.exit(0)
    except Exception as err:
        print(err)


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

    for ticker, premarket_high in zip(tickers, premarket_highs):
        scalper.buy_stock(ticker, premarket_high)

    sys.exit(0)
