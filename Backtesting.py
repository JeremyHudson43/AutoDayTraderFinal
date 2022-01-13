import pandas as pd
from datetime import datetime
import finviz
import os
import time
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

directory = 'C:\\Users\\Frank Einstein\\PycharmProjects\\AutoDaytrader\\small_cap_records'

for file in os.listdir(directory):
    stock = file[:-4]

    data = pd.read_csv(os.path.join(directory, file), index_col = 0)

    data['date'] = pd.to_datetime(data['date'])

    # groupby your key and freq
    g = data.groupby(pd.Grouper(key='date', freq='D'))

    # groups to a list of dataframes with list comprehension
    dfs = [group for _,group in g]
    for df in dfs:
        try:

            date = df['date'].dt.date

            if len(date) > 0:
                date = date.to_list()[0]

            df['date'] = df['date'].dt.time

            premarket_start = datetime.strptime('04:00', '%H:%M').time()
            premarket_end = datetime.strptime('09:30', '%H:%M').time()

            market_end = datetime.strptime('16:00', '%H:%M').time()

            premarket_df = df[df["date"].between(premarket_start, premarket_end)]
            premarket_high = premarket_df['high'].max()

            market_df = df[df["date"].between(premarket_end, market_end)]

            market_high = market_df['high'].max()
            market_low = market_df['low'].min()

            finviz_stock = finviz.get_stock(stock)
            stock_float = value_to_float(finviz_stock['Shs Float'])

            total_premarket_volume = sum(premarket_df['volume'].tolist()) * 100
            five_percent_of_float = stock_float * 0.05

            if len(market_df['open'].to_list()) > 0 and len(premarket_df['open'].to_list()) > 0:
                market_open = market_df['open'].to_list()[0]
                premarket_open = premarket_df['open'].to_list()[0]

                if total_premarket_volume > five_percent_of_float and market_high > premarket_high and \
                       market_open > premarket_open * 1.05 and total_premarket_volume > 150000:

                    df_to_save = pd.DataFrame()

                    print("Stock", stock)
                    print("Market Low", market_low)
                    print("Market High", market_high)
                    print('Market Open', market_open)
                    print('Premarket Open', premarket_open)
                    print("Premarket High", premarket_high)
                    print("Premarket Volume", total_premarket_volume)
                    print('Date', date)
                    print('Market High is ' + str(round((get_percent(market_high, premarket_high) - 100), 2)) + '% higher than Premarket High')

                    df_to_save['stock'] = [stock]
                    df_to_save['market_low'] = [market_low]
                    df_to_save['market_high'] = [market_high]
                    df_to_save['market_open'] = [market_open]
                    df_to_save['premarket_open'] = [premarket_open]
                    df_to_save['premarket_high'] = [premarket_high]
                    df_to_save['premarket_volume'] = [total_premarket_volume]
                    df_to_save['date'] = [date]
                    df_to_save['change_between_highs'] = [round(get_percent(market_high, premarket_high) - 100, 2)]
                    df_to_save.to_csv('C:\\Users\\Frank Einstein\\PycharmProjects\\AutoDaytrader\\small_cap_results\\' + stock + '.csv')

                    sys.exit(0)
        except Exception as err:
            print(err)
            sys.exit(0)

        print(df)
