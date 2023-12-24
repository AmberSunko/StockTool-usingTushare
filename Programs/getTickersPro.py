import re,time
import tushare as ts
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import os
from matplotlib.dates import date2num, num2date
from dearpygui.core import *
from dearpygui.simple import *
import getMACDandKDJ,updateCsv

pro = ts.pro_api('6be67345f8053f5d05ff3e42b7d782875170c1ca5cf400392278b03f')

def stockPriceIntraday(ticker,folder):
    intraday = pro.daily(ts_code=ticker, start_date='20200701', end_date='20201008')
    # print(intraday)

    file = folder + '/' + ticker +'.csv'
    if os.path.exists(file):
        history = pd.read_csv(file,index_col=0)
        intraday = intraday.append(history)

    intraday.sort_index(inplace=True)
    # intraday.index.name='Date'

    intraday.to_csv(file)
    print('Intraday for [' + ticker + '] got.')


def testTickers(tickers,isUseDict,startDate,endDate,dictMA,turnOverIn):
    if not isUseDict["KDJ"] and not isUseDict["MACD"]:
        is_skip=1
    else:is_skip=0
    for i, ticker in enumerate(tickers):
        # if ticker != "002735.SZ":continue
        if ticker[0:3] == "688" or ticker=="000029.SZ":
            continue
        print(i, ticker)
        log(str(i)+' '+ticker)
        try:
            print("%d/%d"%(i+1,len(tickers)),ticker)
            log("%d/%d    %s"%(i+1,len(tickers),ticker))
            scale = 100
            # df = getMACDandKDJ.getOnline(ticker,startDate,endDate)[-scale:]
            df = getMACDandKDJ.import_csv(ticker,is_skip,scale)
            # sign = getMACDandKDJ.pickTickers(ticker,df[['MACD_hist','J']],MA,turnOver,per=50)
            sign = getMACDandKDJ.pickTickers(ticker,df,isUseDict=isUseDict,MA=dictMA,turnOverIn=turnOverIn)
            if sign:
                print('[Ticker_code:' + ticker + '] got.')
                log('[Ticker_code:' + ticker + '] got.')
        except:
            print("**************Error*******************")
            log_error("*****************error*****************")
            pass
    print('Intraday for all stocks got')
    log('Intraday for all stocks got')
        # if i>3:
        #     break


tickersRawData = pro.query('stock_basic', exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
bool = tickersRawData['name'].str.contains(r"^((?!ST).)*$")
tickersRawData=tickersRawData[bool]

tickers = tickersRawData['ts_code'].tolist()

dateToday = datetime.datetime.today().strftime('%Y%m%d')
file = '../Data/TickerListCN/TickerList_'+dateToday+'.csv'
tickersRawData.to_csv(file)
print('Tickers saved.')
# testTickers(tickers,endDate=endDate,startDate=startDate,MA=MA)

# for i, ticker in enumerate(tickers):
#     print(i, ticker)
#     try:
#         print('Interday',i,'/',len(tickers))
#         stockPriceIntraday(ticker,folder='../Data/IntradayCN')
#     except:
#         pass
#     if i>3:
#         break
# stockPriceIntraday('000061.SZ',folder='../Data/IntradayCN')\
# testTickers(['300455.SZ','300456.SZ','600862.SH','600118.SH','000738.SZ','6000893.SH','000547.SZ','300114.SZ','000519.SZ'])

#多只测试
# str=''
# for i, ticker in enumerate(tickers):
#     print(i)
#     if i<50:
#         str+=ticker+','
#     elif i==50:
#         str+=ticker
#     else:break
# print(str)
# intraday = ts.pro_bar(ts_code=str, adj='qfq', start_date='20200701', end_date='20201009')
# intraday = pro.daily(ts_code=str, start_date='20200701', end_date='20201009')
# print(intraday)

#************GUI****************
dictMA={"points":{'Close':False,'ma5':False,'ma10':False,'ma20':False,'ma30':False,'ma60':False,'ma120':False,'ma250':False},"comp":{},"li1":[],"li2":[]}
startDateIn=''
endDateIn=''
isUseDict={"KDJ":False,"MACD":False,"TurnOver":False,"MA":False,"MACD_x":1.1}
turnOverIn={"D2D": {0:None,1:None},"D2N":{0:None,1:None}}
countMA=1
countDownload=0
def update_date(sender, data):
    global startDateIn
    global endDateIn
    if sender=="startDate":
        startDateIn= get_value(sender)
    elif sender=="endDate":
        endDateIn=get_value(sender)
    print("更新日期",startDateIn,endDateIn)
def apply_KDJandMACD(sender, data):
    isUseDict[sender]=get_value(sender)
    if isUseDict["MACD"]==True:
        show_item("MACD_x")
    else:hide_item("MACD_x")
    print("更新KDJ and MACD",isUseDict)

def AddandDeleteMA(sender,data):
    global countMA
    if get_value("启用 MA * > MA *")==True and sender=="add":
        strCount=str(countMA+1)
        strCount1="MA"+str(2*countMA+1)
        strCount2="MA"+str(2*countMA+2)
        if does_item_exist(strCount)==False:
            add_group(strCount,parent="1 1")
            add_combo(strCount1,label=" >",width=80,items=MAType,default_value="ma60",parent=strCount,callback=update_MA)
            add_same_line(spacing=10, name="line"+strCount,parent=strCount)
            add_combo(strCount2,label="",width=80,items=MAType,default_value="ma120",parent=strCount,callback=update_MA)
            countMA+=1
    if get_value("启用 MA * > MA *")==True and sender=="delete":
        strCount=str(countMA)
        if does_item_exist(strCount) and countMA!=1:
            delete_item(strCount)
            countMA-=1


def update_MA(sender, data):
    global countMA
    if get_value("启用 MA * > MA *")==False and get_value("启用 MA 朝下")==False and get_value("启用 MA 朝上")==False:
        isUseDict["MA"]=False
    else : isUseDict["MA"]=True

    # 启用 MA * > MA *
    if does_item_exist("1 1")==False:
            add_group("1 1",before="启用换手率(* Days AVG > * Days AVG)")
    if get_value("启用 MA * > MA *")==True and sender=="add":
        strCount=str(countMA+1)
        strCount1="MA"+str(2*countMA+1)
        strCount2="MA"+str(2*countMA+2)
        if does_item_exist(strCount)==False:
            add_group(strCount,parent="1 1")
            add_combo(strCount1,label=" >",width=80,items=MAType,default_value="ma60",parent=strCount,callback=update_MA)
            add_same_line(spacing=10, name="line"+strCount,parent=strCount)
            add_combo(strCount2,label="",width=80,items=MAType,default_value="ma120",parent=strCount,callback=update_MA)
            countMA+=1
    if get_value("启用 MA * > MA *")==True and sender=="delete":
        strCount=str(countMA)
        if does_item_exist(strCount) and countMA!=1:
            delete_item(strCount)
            countMA-=1
    if get_value("启用 MA * > MA *")==True:
        if does_item_exist("1")==False:
            add_group("1",parent="1 1")
            add_combo("MA1",label=" >",width=80,items=MAType,default_value="ma60",parent="1",callback=update_MA)
            add_same_line(spacing=10, name="line1",parent="1")
            add_combo("MA2",label="",width=80,items=MAType,default_value="ma120",parent="1",callback=update_MA)
        show_item("1 1")
        dictMA["comp"]={}
        for i in range(countMA):
            liTemp=[get_value("MA"+str(2*i+1)),get_value("MA"+str(2*i+2))]
            if i==0 :
                if liTemp[0]!=liTemp[1]:
                    dictMA["comp"][i]=[get_value("MA"+str(2*i+1)),get_value("MA"+str(2*i+2))]
            elif liTemp in dictMA["comp"].values() or liTemp[0]==liTemp[1] or [liTemp[1],liTemp[0]] in dictMA["comp"].values():
                continue
            else: dictMA["comp"][i]=[get_value("MA"+str(2*i+1)),get_value("MA"+str(2*i+2))]
        list2=[]
        for key in dictMA["comp"]:
            if dictMA["comp"][key][0]!= 'Close' and int(dictMA["comp"][key][0][2:]) not in list2:
                list2.append(int(dictMA["comp"][key][0][2:]))
            if dictMA["comp"][key][1]!= 'Close' and int(dictMA["comp"][key][1][2:]) not in list2:
                list2.append(int(dictMA["comp"][key][1][2:]))
        list2.sort()
        dictMA["li2"]=list2
    else:
        hide_item("1 1")
        dictMA["comp"]={}
        dictMA["li2"]=[]
    # *************************************
    if get_value("启用 MA 朝下")==True:
        show_item("downClose")
        show_item("sameline_dw01")
        show_item("downma5")
        show_item("sameline_dw05")
        show_item("downma10")
        show_item("sameline5")
        show_item("downma20")
        show_item("sameline6")
        show_item("downma30")
        show_item("sameline7")
        show_item("downma60")
        show_item("sameline8")
        show_item("downma120")
        show_item("sameline81")
        show_item("downma250")
        if "downma" in sender:
            temp1=get_value(sender)
            print(sender)
            dictMA["points"][sender[4:]]="down" if temp1==True else False
            set_value("up"+sender[4:],False)
    else:
        hide_item("downClose")
        hide_item("sameline_dw01")
        hide_item("downma5")
        hide_item("sameline_dw05")
        hide_item("downma10")
        hide_item("sameline5")
        hide_item("downma20")
        hide_item("sameline6")
        hide_item("downma30")
        hide_item("sameline7")
        hide_item("downma60")
        hide_item("sameline8")
        hide_item("downma120")
        hide_item("sameline81")
        hide_item("downma250")
        for key in dictMA["points"]:
            dictMA["points"][key]=False if dictMA["points"][key]=="down" else dictMA["points"][key]

    if get_value("启用 MA 朝上")==True:
        show_item("upClose")
        show_item("sameline_up01")
        show_item("upma5")
        show_item("sameline_up05")
        show_item("upma10")
        show_item("sameline1")
        show_item("upma20")
        show_item("sameline2")
        show_item("upma30")
        show_item("sameline3")
        show_item("upma60")
        show_item("sameline4")
        show_item("upma120")
        show_item("sameline41")
        show_item("upma250")
        if "upma" in sender:
            temp1=get_value(sender)
            dictMA["points"][sender[2:]]="up" if temp1==True else False
            set_value("down"+sender[2:],False)
    else:
        hide_item("upClose")
        hide_item("sameline_up01")
        hide_item("upma5")
        hide_item("sameline_up05")
        hide_item("upma10")
        hide_item("sameline1")
        hide_item("upma20")
        hide_item("sameline2")
        hide_item("upma30")
        hide_item("sameline3")
        hide_item("upma60")
        hide_item("sameline4")
        hide_item("upma120")
        hide_item("sameline41")
        hide_item("upma250")
        for key in dictMA["points"]:
            dictMA["points"][key]=False if dictMA["points"][key]=="up" else dictMA["points"][key]
    list1=[]
    for key in dictMA["points"]:
        if dictMA["points"][key]:
            # list1.append(int(key[2:]))
            list1.append(key)
    list1.sort()
    dictMA["li1"]=list1
    print("更新MA",dictMA,isUseDict)
MAType = ['Close','ma5','ma10','ma20','ma30','ma60','ma120','ma250']

def apply_turnover(sender, data):
    global turnOverIn
    if get_value("启用换手率(* Days AVG > * Days AVG)")==False and get_value("启用换手率(* Days AVG > * )")==False:
        isUseDict["TurnOver"]=False
    else:isUseDict["TurnOver"]=True
    if get_value("启用换手率(* Days AVG > * Days AVG)")==True:
        show_item("Days1")
        show_item("sameline10")
        show_item("Days2")
        turnOverIn["D2D"][0]=get_value("Days1")
        turnOverIn["D2D"][1]=get_value("Days2")
    else:
        hide_item("Days1")
        hide_item("sameline10")
        hide_item("Days2")
        turnOverIn["D2D"][0]=None
        turnOverIn["D2D"][1]=None
    if get_value("启用换手率(* Days AVG > * )")==True:
        show_item("Days3")
        show_item("sameline11")
        show_item("turnOver per")
        turnOverIn["D2N"][0]=get_value("Days3")
        turnOverIn["D2N"][1]=get_value("turnOver per")
    else:
        hide_item("Days3")
        hide_item("sameline11")
        hide_item("turnOver per")
        turnOverIn["D2N"][0]=None
        turnOverIn["D2N"][1]=None
    print("更新turnOver",turnOverIn,isUseDict)


def apply_theme(sender, data):
    theme = get_value("Themes")
    set_theme(theme)
themes = ["Dark", "Light", "Classic", "Dark 2", "Grey", "Dark Grey", "Cherry", "Purple", "Gold", "Red"]

def show_newlogger(sender,data):
    show_logger()

def startRunning(sender,data):
    log("Start Running")
    print("开始运行",dictMA,isUseDict,startDateIn,endDateIn,turnOverIn)
    run_async_function(long_async_callback, None)
    log('Intraday for all stocks got')

def updateAll(sender,data):
    global countDownload
    if countDownload ==0:
        log("Start Downloading")
        run_async_function(long_async_callback2, None)
        log('Intraday for all stocks got')
        countDownload=1

def long_async_callback(data, sender):
    testTickers(tickers,endDate=endDateIn,startDate=startDateIn,isUseDict=isUseDict,dictMA=dictMA,turnOverIn=turnOverIn)

def long_async_callback2(data, sender):
    updateCsv.startRunning()

with window("Tutorial"):
    set_style_global_alpha(2)
    set_main_window_title("Amber's Demo")
    set_main_window_size(width=900,height=800)
    add_additional_font('Resource/NotoSerifCJKjp-Medium.otf',16,'chinese_simplified_common' )
    add_combo("Themes", items=themes, default_value="Dark", callback=apply_theme)

    add_text("输入日期Input date")
    add_input_text("startDate",label="输入开始日期(例如:20200801)",decimal=True, width=160,callback=update_date)
    add_input_text("endDate",label="输入截止日期",decimal=True,width=160, callback=update_date)
    # add_input_int("Input Int", callback=update_var)
    add_checkbox("MACD", callback=apply_KDJandMACD)
    add_input_float("MACD_x",width=100,label="X系数 (X*B[low]>A[low])",show=False,default_value=1.1,callback=apply_KDJandMACD)

    add_checkbox("KDJ", callback=apply_KDJandMACD)

    add_checkbox("启用 MA 朝上",callback=update_MA)
    add_checkbox("upClose",label="Close", callback=update_MA,show=False)
    add_same_line(spacing=20, name="sameline_up01",show=False)
    add_checkbox("upma5",label="MA5", callback=update_MA,show=False)
    add_same_line(spacing=20, name="sameline_up05",show=False)
    add_checkbox("upma10",label="MA10", callback=update_MA,show=False)
    add_same_line(spacing=20, name="sameline1",show=False)
    add_checkbox("upma20",label="MA20", callback=update_MA,show=False)
    add_same_line(spacing=20, name="sameline2",show=False)
    add_checkbox("upma30", label="MA30",callback=update_MA,show=False)
    add_same_line(spacing=20, name="sameline3",show=False)
    add_checkbox("upma60", label="MA60",callback=update_MA,show=False)
    add_same_line(spacing=20, name="sameline4",show=False)
    add_checkbox("upma120", label="MA120",callback=update_MA,show=False)
    add_same_line(spacing=20, name="sameline41",show=False)
    add_checkbox("upma250", label="MA250",callback=update_MA,show=False)

    add_checkbox("启用 MA 朝下",callback=update_MA)
    add_checkbox("downClose", label="Close",callback=update_MA,show=False)
    add_same_line(spacing=20, name="sameline_dw01",show=False)
    add_checkbox("downma5", label="MA5",callback=update_MA,show=False)
    add_same_line(spacing=20, name="sameline_dw05",show=False)
    add_checkbox("downma10", label="MA10",callback=update_MA,show=False)
    add_same_line(spacing=20, name="sameline5",show=False)
    add_checkbox("downma20",label="MA20", callback=update_MA,show=False)
    add_same_line(spacing=20, name="sameline6",show=False)
    add_checkbox("downma30", label="MA30",callback=update_MA,show=False)
    add_same_line(spacing=20, name="sameline7",show=False)
    add_checkbox("downma60", label="MA60",callback=update_MA,show=False)
    add_same_line(spacing=20, name="sameline8",show=False)
    add_checkbox("downma120", label="MA120",callback=update_MA,show=False)
    add_same_line(spacing=20, name="sameline81",show=False)
    add_checkbox("downma250", label="MA250",callback=update_MA,show=False)

    add_checkbox("启用 MA * > MA *",callback=update_MA)
    add_same_line(name="addline",spacing=16)
    add_button("add",label="+",width=20,callback=update_MA)
    add_same_line(name="deleteline",spacing=10)
    add_button("delete",label="-",width=20,callback=update_MA)

    # add_combo("MA1",label=">",width=80,items=MAType,default_value="MA60",show=False,callback=update_MA)
    # add_same_line(spacing=20, name="sameline9",show=False)
    # add_combo("MA2",label="",width=80,items=MAType,default_value="MA120",show=False,callback=update_MA)

    add_checkbox("启用换手率(* Days AVG > * Days AVG)",callback=apply_turnover)
    add_input_int("Days1",label="Days >",width=80,default_value=1,show=False,callback=apply_turnover)
    add_same_line(spacing=10, name="sameline10",show=False)
    add_input_int("Days2",label="Days",width=80,show=False, callback=apply_turnover)

    add_checkbox("启用换手率(* Days AVG > * )",callback=apply_turnover)
    add_input_int("Days3",label="Days AVG >",width=80,default_value=1,show=False,callback=apply_turnover)
    add_same_line(spacing=10, name="sameline11",show=False)
    add_input_float("turnOver per",label="%    A(100>=A>=0)",show=False,width=120, callback=apply_turnover)

    add_text("确认参数后，点击运行")
    add_button("start",label="运行",width=160,callback=startRunning)
    add_button("显示日志",width=160,callback=show_newlogger)
    add_text("更新数据时，不要点击运行")
    add_button("updateDate",label="更新",width=160,callback=updateAll)
    show_logger()
    set_log_level(mvTRACE)
    set_thread_count(1)
    log("trace message")
    log_debug("debug message")
    log_info("info message")
    log_warning("warning message")
    log_error("error message")




start_dearpygui(primary_window="Tutorial")

