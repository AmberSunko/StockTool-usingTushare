import time
# 图形参数控制
# import pylab as pl
import copy
# 导入及处理数据
import pandas as pd
# 绘图
import matplotlib.pyplot as plt
import matplotlib as mpl
# 解决一些编辑器(VSCode)或IDE(PyCharm)等存在的图片显示问题，
# 应用Tkinter绘图，以便对图形进行放缩操作
# mpl.use('TkAgg')
import datetime
import os
import tushare as ts
from pandas.core.frame import DataFrame


#从api获取数据并处理
pro = ts.pro_api('6be67345f8053f5d05ff3e42b7d782875170c1ca5cf400392278b03f')
def getOnline(stock_code,start_date='',end_date=''):
    # df = pro.daily(ts_code=stock_code, start_date=start_date, end_date=end_date)

    ts.set_token('6be67345f8053f5d05ff3e42b7d782875170c1ca5cf400392278b03f')
    df = ts.pro_bar(ts_code=stock_code, adj='qfq', start_date=start_date, end_date=end_date)

    df.rename(columns={
        'trade_date': 'Date',
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume'
    },
        inplace=True)

    df['Date'] = pd.to_datetime(df['Date'], format='%Y%m%d')
    df.set_index(['Date'], inplace=True)
    df.sort_index(inplace=True)
    return df
# 导入数据并做处理
def import_csv(stock_code,is_skip,scale):
    if is_skip:
        df = pd.read_csv('../Data/ALL/' + stock_code + '.csv',index_col=0,nrows = 2)
    else:
        df = pd.read_csv('../Data/ALL/' + stock_code + '.csv',index_col=0)[:scale]
    df.rename(columns={
        'trade_date': 'Date',
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume'
    },
        inplace=True)

    df['Date'] = pd.to_datetime(df['Date'], format='%Y%m%d')
    df.set_index(['Date'], inplace=True)
    df.sort_index(inplace=True)
    return df

def calculateMACD(df):
    # EMA(Exponential Moving Average), 指数移动平均线
    num_periods_fast = 12  # 快速EMA的时间周期，10
    # K:平滑常数，常取2/(n+1)
    K_fast = 2 / (num_periods_fast + 1)  # 快速EMA平滑常数
    ema_fast = 0
    num_periods_slow = 26  # 慢速EMA的时间周期，40
    K_slow = 2 / (num_periods_slow + 1)  # 慢速EMA平滑常数
    ema_slow = 0
    num_periods_macd = 9  # MACD EMA的时间周期，20
    K_macd = 2 / (num_periods_macd + 1)  # MACD EMA平滑常数
    ema_macd = 0

    ema_fast_values = []
    ema_slow_values = []
    macd_values = []
    macd_signal_values = []
    # MACD - MACD-EMA
    MACD_hist_values = []
    for close_price in df['Close']:
        if ema_fast == 0:  # 第一个值
            ema_fast = close_price
            ema_slow = close_price
        else:
            ema_fast = (close_price - ema_fast) * K_fast + ema_fast
            ema_slow = (close_price - ema_slow) * K_slow + ema_slow

        ema_fast_values.append(ema_fast)
        ema_slow_values.append(ema_slow)

        # MACD is fast_MA - slow_EMA
        macd = ema_fast - ema_slow
        if ema_macd == 0:
            ema_macd = macd
        else:
        # signal is EMA of MACD values
            ema_macd = (macd - ema_macd) * K_macd + ema_macd
        macd_values.append(macd)
        macd_signal_values.append(ema_macd)
        MACD_hist_values.append(macd - ema_macd)

    df = df.assign(ClosePrice=pd.Series(df['Close'], index=df.index))
    df = df.assign(FastEMA10d=pd.Series(ema_fast_values, index=df.index))
    df = df.assign(SlowEMA40d=pd.Series(ema_slow_values, index=df.index))
    df = df.assign(MACD=pd.Series(macd_values, index=df.index))
    df = df.assign(EMA_MACD20d=pd.Series(macd_signal_values, index=df.index))
    df = df.assign(MACD_hist=pd.Series(MACD_hist_values, index=df.index))

    return df
def calculateKDJ(df):
    low_list = df['Low'].rolling(9, min_periods=9).min()
    low_list.fillna(value = df['Low'].expanding().min(), inplace = True)
    high_list = df['High'].rolling(9, min_periods=9).max()
    high_list.fillna(value = df['High'].expanding().max(), inplace = True)
    rsv = (df['Close'] - low_list) / (high_list - low_list) * 100

    df['K'] = pd.DataFrame(rsv).ewm(com=2).mean()
    df['D'] = df['K'].ewm(com=2).mean()
    df['J'] = 3 * df['K'] - 2 * df['D']
    return df

def useMACD(df,x=1.1,per=50):
    # print("MA",MA,"turn",turnover)
    # dfNew = df.sort_index(ascending=False)
    if(df['MACD_hist'][0]<0):
        count = 0
        countarea = [] #区域数量
        area = 0 #面积
        maxDown1 = []
        minDown1= []
        maxDown2 = []
        minDown2= []
        delta= 0
        type = 0
        for index ,value in df['MACD_hist'].items() :
            # print('maxDown1:',maxDown1,'minDown1:',minDown1,'maxDown2:',maxDown2,'minDown2:',minDown2)
            # print(count,index,value,countarea)
            if count==0:
                area += value
                maxDown1 = [count,value]
                delta= maxDown1[1]/per
                minDown1= [count,value]
            elif (value-delta)*(df['MACD_hist'][count-1]-delta)>=0:
                # print(count,value, delta)
                if len(countarea)==0:
                    maxDown1 = maxDown1 if maxDown1[1] < value else [count,value]
                    delta= maxDown1[1]/per
                    minDown1 = minDown1 if minDown1[1] > value else [count,value]
                elif len(countarea)==2:
                    maxDown2 = maxDown2 if maxDown2[1] < value else [count,value]
                    minDown2 = minDown2 if minDown2[1] > value else [count,value]
                area += value
            elif (value-delta)*(df['MACD_hist'][count-1]-delta)<0:
                if len(countarea)==3:
                    break
                else:
                    countarea.append(area)
                    area =value
                    if len(countarea)==2:
                        maxDown2 = [count,value]
                        minDown2= [count,value]

            count+=1
        if(countarea[0]-countarea[-1])>0 and x*df.iloc[maxDown2[0]]["Low"]>df.iloc[maxDown1[0]]["Low"]:
            return True
        else:
            return False
    else:
        return False


def getTurnover(stock_code,turnOverIn,df):
    # df = import_csv(stock_code)
    # df = pro.daily_basic(ts_code=stock_code, trade_date='', fields='ts_code,trade_date,turnover_rate')
    if turnOverIn["D2D"][0]:
        if df['turnover_rate'].head(turnOverIn["D2D"][0]).mean() <= df['turnover_rate'].head(turnOverIn["D2D"][1]).mean():
            print("F D2D",df['turnover_rate'].head(turnOverIn["D2D"][0]).mean(),df['turnover_rate'].head(turnOverIn["D2D"][1]).mean())
            return False
    if turnOverIn["D2N"][0]:
        if df['turnover_rate'].head(turnOverIn["D2N"][0]).mean() <= turnOverIn["D2N"][1]:
            print("F D2N",df['turnover_rate'].head(turnOverIn["D2N"][0]).mean(),turnOverIn["D2N"][1])
            return False
    return True

def getMA(stock_code,MA,df):
    dateToday = datetime.datetime.today().strftime('%Y%m%d')
    # df = ts.pro_bar(ts_code=stock_code, adj='qfq',start_date='', end_date=dateToday, ma=MA["li1"]).head(2)
    for i,value in enumerate(MA["li1"]):
        if MA["points"][value]=="up":
            if df.iloc[0][value]>df.iloc[1][value]:
                continue
            else:
                print("F",value,"UP")
                return False
        elif MA["points"][value]=="down":
            if df.iloc[0][value]<df.iloc[1][value]:
                continue
            else:
                print("F",value,"DOWN")
                return False
    comp1=''
    comp2=''
    if MA["comp"]:
        # df= ts.pro_bar(ts_code=stock_code, adj='qfq',start_date='', end_date=dateToday, ma=MA["li2"]).head(1)
        for key in MA["comp"]:
            comp1 = MA["comp"][key][0]
            comp2 = MA["comp"][key][1]
            if df.iloc[0][comp1] != df.iloc[0][comp1] or df.iloc[0][comp2] != df.iloc[0][comp2] :
                print("F",comp1,":",df.iloc[0][comp1],comp2,":",df.iloc[0][comp2])
                return False
            if df.iloc[0][comp1]<=df.iloc[0][comp2]:
                print("F",comp1,":",df.iloc[0][comp1],comp2,":",df.iloc[0][comp2])
                return False

    return True

def getMACDPlot(df,stock_code):
    close_price = df['ClosePrice']
    ema_f = df['FastEMA10d']
    ema_s = df['SlowEMA40d']
    macd = df['MACD']
    ema_macd = df['EMA_MACD20d']
    macd_hist = df['MACD_hist']
    K = df['K']
    D = df['D']
    J = df['J']
    # 设置画布，纵向排列的三个子图
    fig, ax = plt.subplots(4, 1)

    # 设置标签显示中文
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False

    # 调整子图的间距，hspace表示高(height)方向的间距
    plt.subplots_adjust(hspace=.1)

    # 设置第一子图的y轴信息及标题
    ax[0].set_ylabel('Close price in ￥')
    ax[0].set_title('A_Stock %s MACD Indicator' % stock_code)
    close_price.plot(ax=ax[0], color='g', lw=1., legend=True, use_index=False)
    ema_f.plot(ax=ax[0], color='b', lw=1., legend=True, use_index=False)
    ema_s.plot(ax=ax[0], color='r', lw=1., legend=True, use_index=False)

    # 应用同步缩放
    ax[1] = plt.subplot(412, sharex=ax[0])
    macd.plot(ax=ax[1], color='k', lw=1., legend=True, sharex=ax[0], use_index=False)
    ema_macd.plot(ax=ax[1], color='g', lw=1., legend=True, use_index=False)

    # 应用同步缩放
    ax[2] = plt.subplot(413, sharex=ax[0])
    macd_hist.plot(ax=ax[2], color='r', kind='bar', legend=True, sharex=ax[0])

    ax[3] = plt.subplot(414, sharex=ax[0])
    K.plot(ax=ax[3], color='b', lw=1.,  legend=True,use_index=False, sharex=ax[0])
    D.plot(ax=ax[3], color='y', lw=1., legend=True,use_index=False, sharex=ax[0])
    J.plot(ax=ax[3], color='r', lw=1., legend=True,use_index=False, sharex=ax[0])

    # 设置间隔，以便图形横坐标可以正常显示（否则数据多了x轴会重叠）
    # interval = scale // 20
    # print(pd.date_range(df.index[0], df.index[99]))
    # print([i for i in range(1, scale + 1, interval)],[datetime.strftime(i, format='%Y-%m-%d') for i in \
    #            pd.date_range(df.index[0], df.index[-1], freq='%dd' % (interval))])

    # 设置x轴参数，应用间隔设置
    # 时间序列转换，(否则日期默认会显示时分秒数据00:00:00)
    # x轴标签旋转便于显示

    # pl.xticks([i for i in range(1, scale + 1, interval)],
    #           [datetime.strftime(i, format='%Y-%m-%d') for i in \
    #            pd.date_range(df.index[0], df.index[-32], freq='%dd' % (interval))],
    #           rotation=45)
    plt.show()
def pickTickers(stock_code,df,isUseDict,turnOverIn,MA):
    dfNew=df
    if isUseDict["KDJ"]:
        dfNewKDJ=calculateKDJ(dfNew).sort_index(ascending=False)#倒序
        if dfNewKDJ["J"][0]<=dfNewKDJ["J"][1]:
            print("F KDJ")
            return False
    if isUseDict["MACD"]:
        dfNewMACD=calculateMACD(dfNew).sort_index(ascending=False)#倒序
        if useMACD(dfNewMACD[['Low','MACD_hist']],isUseDict["MACD_x"])==False:
            print("F MACD")
            return False
    if isUseDict["TurnOver"]:
        dfNewTurnovr=dfNew.sort_index(ascending=False)#倒序
        if getTurnover(stock_code,turnOverIn,dfNewTurnovr)==False:
            return False
    if isUseDict["MA"]:
        dfNewMA=dfNew.sort_index(ascending=False)#倒序
        if getMA(stock_code,MA,dfNewMA)==False:
            return False

    dictPick=DataFrame({"code":[stock_code]})
    dateToday = datetime.datetime.today().strftime('%Y%m%d')
    file = '../Data/MACDpoint/Tickerpick_'+dateToday+'.csv'
    if os.path.exists(file):
        history = pd.read_csv(file,index_col=0)
        dictPick = dictPick.append(history).drop_duplicates(subset='code',keep='first')
    dictPick.to_csv(file)
    return True
# 测试
# stock_code = '000692.SZ'
# isUseDict={"KDJ":True,"MACD":True,"TurnOver":True,"MA":True,"MACD_x":1.1}
# # df = ts.pro_bar(ts_code=stock_code, adj='qfq',start_date='', end_date="20201103", ma=[10,60])
# dictMA={'points': {'MA10': False, 'MA20': False, 'MA30': False, 'MA60': "up", 'MA120': False ,'MA250':"up"}, 'comp': {}, 'li1': [60,120], 'li2': []}
# turnOverIn={"D2D": {0:1,1:5},"D2N":{0:1,1:1.0}}
# df = import_csv(stock_code)[-100:]
# print(pickTickers(stock_code,df,isUseDict=isUseDict,MA=dictMA,turnOverIn=turnOverIn))
# df=calculateMACD(df).sort_index(ascending=False)
# print(useMACD(df[["Low","MACD_hist"]]))
# df = getTurnover(stock_code,turnOverIn,df.sort_index(ascending=False))


# # getMACDPlot(df,stock_code)