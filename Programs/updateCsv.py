import tushare as ts
import pandas as pd
import datetime
import os
import threading,time,math

sign=0
exitFlag =0
pro = ts.pro_api('6be67345f8053f5d05ff3e42b7d782875170c1ca5cf400392278b03f')
ts.set_token('6be67345f8053f5d05ff3e42b7d782875170c1ca5cf400392278b03f')
dateToday = datetime.datetime.today().strftime('%Y%m%d')
startDate = pro.trade_cal(exchange='SSE', is_open='1',
                        start_date="",
                        end_date=dateToday,
                        fields='cal_date').sort_index(ascending=False).head(260).iloc[-1]["cal_date"]
tickersRawData = pro.query('stock_basic', exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
bool = tickersRawData['name'].str.contains(r"^((?!ST).)*$")
tickersRawData=tickersRawData[bool]
tickers = tickersRawData['ts_code'].tolist()
threadLock = threading.Lock()
count=0
countA=0
countB=0
timeCount=None
class myThread (threading.Thread):
    def __init__(self, threadID,li=[]):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.li=li
        self._stop_event = threading.Event()
    def run(self):
        print ("开始线程：" + self.name)
        downLoad(self.threadID,self.li)
        print ("退出线程：" + self.name)
    def stop(self):
        self._stop_event.set()

def downLoad(threadID,tickerHalf):
    global exitFlag
    global count
    global tickers
    global timeCount
    global countA,countB
    for i, ticker in enumerate(tickerHalf):
        try:
            threadLock.acquire()
            if(threadID==1):
                countA=i+1
                print("%d/%d"%(i+1+countB,len(tickers)),ticker)
            else:
                countB=i+1
                print("%d/%d"%(i+1+countA,len(tickers)),ticker)
            count=count+1
            # print("before",count,time.perf_counter()-timeCount)
            if count>=201:
                count=1
                if (time.perf_counter()-timeCount)<60:
                    print("暂停:",61-time.perf_counter()+timeCount," s")
                    time.sleep(61-time.perf_counter()+timeCount)
                timeCount=time.perf_counter()
            threadLock.release()
            # print("after",count,time.perf_counter()-timeCount)
            stockPriceIntraday(ticker,folder='../Data/ALL')
        except:
            print("error")
            pass

def stockPriceIntraday(ticker,folder):
    global startDate,dateToday
    intraday = ts.pro_bar(ts_code=ticker, adj='qfq', start_date=startDate, end_date=dateToday,ma=[5,10,20,30,60,120,250], factors=['tor'])
    # print(intraday)
    file = folder + '/' + ticker +'.csv'
    # if os.path.exists(file):
    #     history = pd.read_csv(file,index_col=0)
    #     intraday.append(history).drop_duplicates(subset='trade_date',keep='first')

    intraday.sort_index(inplace=True)
    # intraday.index.name='Date'

    intraday.to_csv(file)
    print('Intraday for [' + ticker + '] got.')

def stockPriceIntraday_Single(ticker,folder):
    global dateToday
    intraday = ts.pro_bar(ts_code=ticker, adj='qfq', end_date=dateToday,ma=[10,20,30,60,120,250], factors=['tor'])
    # print(intraday)
    file = folder + '/' + ticker +'.csv'
    # if os.path.exists(file):
    #     history = pd.read_csv(file,index_col=0)
    #     intraday.append(history).drop_duplicates(subset='trade_date',keep='first')

    intraday.sort_index(inplace=True)
    # intraday.index.name='Date'

    intraday.to_csv(file)
    print('Intraday for [' + ticker + '] got.')

def startRunning():
    global timeCount
    global sign
    sign=1
    timeCount=time.perf_counter()
    thread1 = myThread(1,tickers[0:math.ceil(len(tickers)/2)])
    thread2 = myThread(2,tickers[math.ceil(len(tickers)/2):])
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()
    print('Intraday for all stocks got')

# stockPriceIntraday_Single("300168.SZ","../Data/ALL")
# startRunning()