import numpy as np
import pandas as pd
from datetime import datetime
import finviz
import os
import time
import sys
import plotly.graph_objects as go
from os.path import exists
import traceback


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

directory = 'C:\\Users\\Frank Einstein\\PycharmProjects\\AutoDaytrader\\small_cap_records_days'

results_dir = 'C:\\Users\\Frank Einstein\\PycharmProjects\\AutoDaytrader\\small_cap_results_days'

for file in os.listdir(directory):

    stock = file[:-4]

    if stock not in [x[:-4] for x in os.listdir(results_dir)]:

        data = pd.read_csv(os.path.join(directory, file), index_col = 0)

        data['date'] = pd.to_datetime(data['date'])

        # groupby your key and freq
        g = data.groupby(pd.Grouper(key='date', freq='D'))

        # groups to a list of dataframes with list comprehension
        dfs = [group for _,group in g]
        for df in range(len(dfs)):
            try:

                dataframe_obj = dfs[df]
                yesterday_close = dfs[df - 1]

                date = dataframe_obj ['date'].dt.date

                if len(date) > 0:
                    date = date.to_list()[0]

                dataframe_obj['date'] = dataframe_obj['date'].dt.time

                premarket_start = datetime.strptime('04:00', '%H:%M').time()
                premarket_end = datetime.strptime('09:30', '%H:%M').time()

                market_end = datetime.strptime('16:00', '%H:%M').time()

                premarket_df = dataframe_obj[dataframe_obj["date"].between(premarket_start, premarket_end)]
                premarket_high = premarket_df['high'].max()

                market_df = dataframe_obj[dataframe_obj ["date"].between(premarket_end, market_end)]

                market_high = market_df['high'].max()
                market_low = market_df['low'].min()

                finviz_stock = finviz.get_stock(stock)
                stock_float = value_to_float(finviz_stock['Shs Float'])

                total_premarket_volume = sum(premarket_df['volume'].tolist()) * 100
                five_percent_of_float = stock_float * 0.05

                low_prices = []

                if len(market_df['open'].to_list()) > 0 and len(premarket_df['open'].to_list()) > 0 \
                        and len(yesterday_close['close'].to_list()) > 0:

                    market_open = market_df['open'].to_list()[0]
                    premarket_open = premarket_df['open'].to_list()[0]

                    yesterday_close = yesterday_close['close'].to_list()[-1]

                    vf_ratio = get_percent(total_premarket_volume, stock_float)

                    if market_open >= yesterday_close * 1.05 and market_high > premarket_high and vf_ratio > 5:

                        market_df = dataframe_obj[dataframe_obj["date"].between(premarket_end, market_end)]

                        price_to_keep = 0

                        bought = False
                        stop_loss = False
                        take_profit = False

                        for index, row in market_df.iterrows():
                            if row['high'] >= premarket_high * 1.005 and not bought:
                                bought = True
                                price_to_keep = row['high']
                            if row['low'] >= premarket_high * 1.005 and not bought:
                                bought = True
                                price_to_keep = row['low']
                            if row['open'] >= premarket_high * 1.005 and not bought:
                                bought = True
                                price_to_keep = row['open']
                            if row['close'] >= premarket_high * 1.005 and not bought:
                                bought = True
                                price_to_keep = row['close']

                        if bought and index > 0:
                            print('index' ,index)
                            # time.sleep(5)

                            market_df_final = market_df

                            market_df_final['bought'] = market_df['close'] >= price_to_keep

                            market_df_final = market_df_final[market_df_final['bought'] == True]

                            print(market_df_final)

                            time.sleep(1)

                            market_df_final['highest'] = market_df_final['close'].cummax()  # take the cumulative max
                            market_df_final['trailingstop'] = market_df_final['highest'] * 0.95  # subtract 1% of the max
                            market_df_final['exit_signal'] = market_df_final['close'] < market_df_final['trailingstop']

                            market_df_final = market_df_final[market_df_final['exit_signal'] == True].iloc[0]

                            trailing_stop = market_df_final['trailingstop']

                            print('Trailing Stop', trailing_stop, 'PM High', premarket_high)


                            df_to_save = pd.DataFrame()

                            # lowest_price_after_PM_high_break = round(min(low_prices), 2)

                            print("Stock", stock)
                            print("Market Low", market_low)
                            print("Market High", market_high)
                            print('Market Open', market_open)
                            print('Yesterday Close', yesterday_close)
                            print("Premarket High", premarket_high)
                            print("Premarket Open", premarket_open)
                            print("Premarket Volume", total_premarket_volume)
                            print('Date', date)
                            print('Market High is ' + str(round((get_percent(market_high, premarket_high) - 100), 2)) + '% higher than Premarket High')
                            print('Market Low is ' + str(round(get_percent(market_high, market_low) - 100, 2)) + '% lower than Market High')
                            print('Market Low is ' + str(round(get_percent(market_high, premarket_high) - 100, 2)) + '% lower than Premarket High')
                            # print('Lowest price after breaking above Premarket High is ' + str(lowest_price_after_PM_high_break))
                            print('Bought?', bought)
                            print('Stop Loss?', stop_loss)
                            print('Take Profit?', take_profit)
                            print('V/F Ratio', round(vf_ratio, 2))
                            print('Trailing Stop', trailing_stop)

                            df_to_save['stock'] = [stock]
                            df_to_save['market_low'] = [market_low]
                            df_to_save['market_high'] = [market_high]
                            df_to_save['market_open'] = [market_open]
                            df_to_save['yesterday_close'] = [yesterday_close]
                            df_to_save['premarket_high'] = [premarket_high]
                            df_to_save['premarket_open'] = [premarket_open]
                            df_to_save['premarket_volume'] = [total_premarket_volume]
                            df_to_save['date'] = [date]
                            df_to_save['change_perc_between_highs'] = [round(get_percent(market_high, premarket_high) - 100, 2)]
                            df_to_save['market_high_to_market_low'] = [round(get_percent(market_high, market_low) - 100, 2)]
                            df_to_save['market_low_to_premarket_high'] = [round(get_percent(market_high, premarket_high) - 100, 2)]
                            # df_to_save['lowest_price_after_breaking_above_premarket_high'] = [round(min(low_prices), 2)]
                            # df_to_save['lowest_price_after_breaking_above_premarket_high_perc_diff'] = \
                                # round(get_percent(lowest_price_after_PM_high_break, premarket_high) - 100, 2)
                            df_to_save['bought'] = [bought]
                            df_to_save['stop_loss'] = [stop_loss]
                            df_to_save['take_profit'] = [take_profit]
                            df_to_save['stock_float'] = [stock_float]
                            df_to_save['VF_Ratio'] = [round(vf_ratio, 2)]
                            df_to_save['trailing_stop'] = [trailing_stop]

                            csv_path = 'C:\\Users\\Frank Einstein\\PycharmProjects\\AutoDaytrader\\small_cap_results_days\\' + stock + '.csv'

                            if not exists(csv_path):
                                df_to_save.to_csv(csv_path)
                            else:
                                pd.read_csv(csv_path).append(df_to_save).to_csv(csv_path, index=False)

                            # print market data as candle chart

                            # add a horizontal line to indicate the buy time at half a percent higher than premarket high
                            # add a horizontal line to indicate the stop loss at 1.5% lower than premarket high
                            # add a horizontal line to indicate the buy time at half a percent lower than premarket low
                            layout = {
                                "xaxis": {
                                    "rangeslider": {
                                        "visible": False
                                    }
                                }
                            }

                            limit_price = float(str(round(premarket_high * 1.005, 2)))
                            take_profit = float(str(round(premarket_high * 1.155, 2)))
                            stop_loss_price = float(str(round(premarket_high * 0.995, 2)))

                            fig = go.Figure(data=[go.Candlestick(x=market_df['date'],
                                                              open=market_df['open'],
                                                              high=market_df['high'],
                                                              low=market_df['low'],
                                                              close=market_df['close'])],
                                         layout=layout)

                            fig.add_hrect(y0=stop_loss_price, y1=limit_price, line_width=0, fillcolor="red",
                                           opacity=0.2)

                            fig.add_hrect(y0=limit_price, y1=take_profit, line_width=0, fillcolor="blue",
                                           opacity=0.2)

                            fig.add_hline(y=limit_price, annotation_text="Premarket High * 1.005")

                            fig.write_image("graph_records\\" + stock + ".png", width=600, height=350, scale=2)

            except Exception as err:
               print(traceback.format_exc())

        print(df)
