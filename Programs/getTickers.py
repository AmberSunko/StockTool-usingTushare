import tushare as ts
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import os
from matplotlib.dates import date2num, num2date

def stockPriceIntraday(ticker,folder):
    intraday = ts.get_hist_data(ticker,ktype='60')
    # print(intraday)

    file = folder + '/' + ticker +'.csv'
    if os.path.exists(file):
        history = pd.read_csv(file,index_col=0)
        intraday.append(history)

    intraday.sort_index(inplace=True)
    # intraday.index.name='Date'

    intraday.to_csv(file)
    print('Intraday for [' + ticker + '] got.')




tickersRawData = ts.get_stock_basics()
tickers = tickersRawData.index.tolist()

dateToday = datetime.datetime.today().strftime('%Y%m%d')
file = '../Data/TickerListCN/TickerList_'+dateToday+'.csv'
tickersRawData.to_csv(file)
print('Tickers saved.')

# for i, ticker in enumerate(tickers):
#     print(i,ticker)
#     try:
#         print('Interday',i,'/',len(tickers))
#         stockPriceIntraday(ticker,folder='../Data/IntradayCN')
#     except:
#         pass
#     if i>3:
#         break
stockPriceIntraday('300168',folder='../Data/IntradayCN')
print('Intraday for all stocks got')