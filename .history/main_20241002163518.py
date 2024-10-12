import sys
import os
from pathlib import Path
import numpy as np
import pandas as pd
import datetime 
import re
import time
from loguru import logger

#log dir
logger.add("file_1.log", rotation="1 MB")

WorkPath = str(Path(os.path.realpath(__file__)).parent)
ModulePath = WorkPath+"\\Modules"
DataPath = WorkPath+"\\Data"
sys.path.append(ModulePath)

from Modules import *

#主程序
if __name__ == "__main__":

    #end on today or yesterday
    EndDate = datetime.date.today()
    if time.localtime().tm_hour < 18:
        delta = datetime.timedelta(days=1)
        EndDate = EndDate-delta
    # start from 365 days ago
    Days = 365
    delta = datetime.timedelta(days=Days)
    StartDate =  EndDate-delta
   
    StartDate = str(StartDate).replace('-','')
    EndDate = str(EndDate).replace('-','')
   
    #get-----
    CodeShangzheng = "000001"
    KLineShangzheng = get_k_history(CodeShangzheng, StartDate, EndDate)

    #获取各个上证A股票------
    # list of stock codes
    Codes = [str(i) for i in range(600000,,606000)]
    #used for debug
    #Codes = [str(600000),str(600004),str(600007)]

    # 股票数据表格
    KLines = pd.DataFrame()
    for Code in Codes:
        print(f'fetching kline data of: {Code} ')
        KLineNew = get_k_history(Code, StartDate, EndDate)
        KLines = pd.concat([KLines,KLineNew],ignore_index=True)
    KLines.sort_values(by="股票代码")

    #检查是否有非数字，如果有，替换为-99999
    Mask =KLines.loc[:,'动态市盈率（昨日）'].apply(not_number)
    KLines.loc[Mask,'动态市盈率（昨日）'] = -99999

    #保存
    StocksTable = '{}\\Stocks{}.csv'.format(DataPath,EndDate)
    KLines.to_csv(StocksTable,encoding='utf-8-sig')
    SZTable = '{}\\SZ{}.csv'.format(DataPath,EndDate)
    KLineShangzheng.to_csv(SZTable,encoding='utf-8-sig')
    
    print('finish saving stock data')
    #------

    #analysis
    GoodStocks = is_recent_good(StocksTable)  
    GoodStocks.to_csv(WorkPath+'\\good stocks.csv',encoding='utf-8-sig')
    print("finish saving good-stock table")

    BadStocks = is_recent_bad(StocksTable) 
    BadStocks.to_csv(WorkPath+'\\bad stocks.csv',encoding='utf-8-sig')
    print("finish saving bad-stock table")

    PulledUpStocks = is_recent_pulled_up(StocksTable)
    PulledUpStocks.to_csv(WorkPath+'/pulled up stocks.csv',encoding='utf-8-sig')
    print("finish saving pulled-up-stock table")