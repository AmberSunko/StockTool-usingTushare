import tushare as ts
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
from matplotlib.dates import date2num, num2date

import time



start = '2020-1-1'
end = '2020-10-5'
tickersRawData = ts.get_stock_basics()
data = ts.get_hist_data('600519')
data=data.sort_values(by='date')
data['Returns']=data['close'].pct_change()
clean_returns=data['Returns'].dropna()
clean_returns.plot()
return_daily = np.mean(clean_returns)
print(tickersRawData)
plt.hist(clean_returns,bins=(len(data)-1))
# plt.show()

close = data['close']
close = close.reset_index()
print(close['date'])
close['date'] = date2num(close['date']).strftime('%Y-%m-%d %H:%M:%S')
# print(data)
