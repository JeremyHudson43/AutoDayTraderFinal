from ib_insync.contract import Stock
from ib_insync.ib import IB
import pandas as pd
import random
import plotly.graph_objects as go
from datetime import datetime
from matplotlib import pyplot as plt
from bs4 import BeautifulSoup


def get_percent(first, second):
    if first == 0 or second == 0:
        return 0
    else:
        percent = first / second * 100
    return percent


ib = IB()

ib.connect('127.0.0.1', 7497, clientId=random.randint(0, 300))

stock = 'EFOI'

security = Stock(stock, 'SMART', 'USD')

year = '2021'
month = '12'
day = '08'

premarket_date = year + month + day + ' 09:29:00'

market_date = year + month + day + ' 16:00:00'

# Fetching historical data when market is closed for testing purposes
premarket_data = pd.DataFrame(
    ib.reqHistoricalData(
        security,
        endDateTime=premarket_date,
        durationStr='1 D',
        barSizeSetting='1 min',
        whatToShow="TRADES",
        useRTH=False,
        formatDate=1
    ))

# Fetching historical data when market is closed for testing purposes
market_data = pd.DataFrame(
    ib.reqHistoricalData(
        security,
        endDateTime=market_date,
        durationStr='1 D',
        barSizeSetting='1 min',
        whatToShow="TRADES",
        useRTH=True,
        formatDate=1
    ))


premarket_high = premarket_data['high'].max()

volume = sum(premarket_data['volume'].tolist()) * 100

# request the fundamentals
fundamentals = ib.reqFundamentalData(security, 'ReportSnapshot')

soup = BeautifulSoup(str(fundamentals), 'xml')

shares = soup.find('SharesOut').text
shares = float(shares)

ratio = get_percent(volume, shares)

if ratio > 5:
    limit_price = float(str(round(premarket_high * 1, 2)))
    take_profit = float(str(round(premarket_high * 1.10, 2)))
    stop_loss_price = float(str(round(premarket_high * 0.98, 2)))

    # print market data as candle chart

    # add a horizontal line to indicate the buy time at half a percent higher than premarket high
    # add a horizontal line to indicate the stop loss at 1.5% lower than premarket high
    # add a horizontal line to indicate the buy time at half a percent lower than premarket low

    print(market_data)

    layout = {
                "xaxis": {
                    "rangeslider": {
                        "visible": False
                    }
                }
             }

    fig = go.Figure(data=[go.Candlestick(x=market_data['date'],
                    open=market_data['open'],
                    high=market_data['high'],
                    low=market_data['low'],
                    close=market_data['close'])],
                    layout=layout)

    fig.add_hrect(y0=stop_loss_price, y1=limit_price, line_width=0, fillcolor="red",
                  opacity=0.2, annotation_text="stop / limit ratio")

    fig.add_hrect(y0=limit_price, y1=take_profit, line_width=0, fillcolor="blue",
                  opacity=0.2, annotation_text="limit / profit ratio")

    fig.add_hline(y=premarket_high, annotation_text="Premarket High")

    fig.write_image("graph_records\\" + stock + ".png", width=600, height=350, scale=2)

    plt.show()

else:
    print('Volume is not high enough to trade')

# print(market_data)
# print(premarket_data)
