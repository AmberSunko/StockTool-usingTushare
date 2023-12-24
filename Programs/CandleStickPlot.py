import pandas as pd
import matplotlib
import mplfinance
import matplotlib.dates
import matplotlib.pyplot as plt
from cycler import cycler

def stockPricePlot(ticker):
    history = pd.read_csv('../Data/IntradayCN/' + ticker + '.csv')
    history.rename(
            columns={
            'date': 'Date', 'open': 'Open',
            'high': 'High', 'low': 'Low',
            'close': 'Close', 'volume': 'Volume'},
            inplace=True)
    history['Date'] = pd.to_datetime(history['Date'])
    history.set_index(['Date'], inplace=True)
    print(history[['Open','Close','High','Low']])

    kwargs = dict(
	type='candle',
	mav=(7, 30, 60),
	volume=True,
    title='\nA_stock %s candle_line' % (ticker),
	ylabel='OHLC Candles',
	ylabel_lower='Shares\nTraded Volume',
	figratio=(15, 10),
	figscale=5)

    mc = mplfinance.make_marketcolors(
	up='red',
	down='green',
	edge='i',
	wick='i',
	volume='in',
	inherit=True)

    s = mplfinance.make_mpf_style(
	gridaxis='both',
	gridstyle='-.',
	y_on_right=False,
	marketcolors=mc)


    # close = history['Close']
    # close= close.reset_index()
    # close['Date'] = close['Date'].map(matplotlib.dates.date2num)
    # print(close['timestamp'])
    #
    # ohlc = history[['Open','Close','High','Low']].resample('1H').ohlc()
    # print(history[['open','close','high','low']].resample('1H').ohlc())
    # ohlc= ohlc.reset_index()
    # ohlc['date'] = ohlc['date'].map(matplotlib.dates.date2num)
    # # print(ohlc.values)
    mplfinance.plot(history,**kwargs,style=s)
    #
    # subplot1 = plt.subplot2grid((2,1),(0,0),rowspan=1,colspan=1)
    # subplot1.xaxis_date()
    # subplot1.plot(close['date'],close['close'],'b.')
    # plt.title(ticker)
    #
    # subplot2 = plt.subplot2grid((2,1),(1,0),rowspan=1,colspan=1)
    # mplfinance.plot(ohlc.values,type='candle',style='charles',show_nontrading=True)
    # subplot2.plot(close['Date'],close['close'],'b.')

    # plt.show()


stockPricePlot('600031')