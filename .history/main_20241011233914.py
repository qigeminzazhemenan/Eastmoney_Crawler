import sys
import os
from pathlib import Path
import numpy as np
import pandas as pd
import datetime 
import re
import time
from loguru import logger
from Modules import *

#---
def main():
    WorkPath = str(Path(os.path.realpath(__file__)).parent)
    ModulePath = WorkPath+"\\Modules"
    DataPath = WorkPath+"\\Data"
    sys.path.append(ModulePath)

    #log dir
    logger.add('{}\\{}'.format(WorkPath,'log.log'), rotation="1 MB")



    #end on today or yesterday
    EndDate = datetime.date.today()
    if time.localtime().tm_hour < 18:
        Delta = datetime.timedelta(days=1)
        EndDate = EndDate-Delta
    #if exist hostory data, start from last day recorded
    if os.listdir(DataPath):
        History = pd.read_csv('{}\\{}'.format(DataPath,os.listdir(DataPath)[0]))
        StartDate = max(History.loc[:'Date'])
    else:
    #if no history data, start from 365 days ago
        Delta = datetime.timedelta(days=365)
        StartDate = EndDate-Delta

    StartDate = str(StartDate).replace('-','')
    EndDate = str(EndDate).replace('-','')

    #get SSE Composite-----
    CodeSSE = "000001"
    KLineSSE = get_k_history(CodeSSE, StartDate, EndDate)

    #get SSE Stocks ------
    # list of stock codes
    Codes = [str(i) for i in range(600000,609000)]
    #used for debug
    Codes = [str(600000),str(600004)]

    #write into stock table
    KLines = pd.DataFrame()
    for Code in Codes:
        print(f'fetching kline data of: {Code} ')
        KLineNew = get_k_history(Code, StartDate, EndDate)
        KLines = pd.concat([KLines,KLineNew],ignore_index=True)
    KLines.sort_values(by=['Stock Code','Date'])

    #check if there is NaN
    #Mask =KLines.groupby('Stock Code').apply(not_number)
    

    #save
    try:
        StocksTable = '{}\\Stocks{}.csv'.format(DataPath,EndDate)
        KLines.to_csv(StocksTable,encoding='utf-8-sig')
        SSETable = '{}\\SZ{}.csv'.format(DataPath,EndDate)
        KLineSSE.to_csv(SSETable,encoding='utf-8-sig')
        logger.success('finish saving stock data')
    except Exception as Error:
        logger.error('meet error when saving stock data table,Error:{}'.format(Error))
    #------

    #analysis
    try:
        GoodStocks = is_recent_good(StocksTable)  
        GoodStocks.to_csv(WorkPath+'\\good stocks.csv',encoding='utf-8-sig')
        logger.success("finish saving recent-good-stock table")
    except Exception as Error:
        logger.error('meet error when saving recent-good-stock table,Error:{}'.format(Error))

    try:
        BadStocks = is_recent_bad(StocksTable) 
        BadStocks.to_csv(WorkPath+'\\bad stocks.csv',encoding='utf-8-sig')
        logger.success("finish saving recent-bad-stock table")
    except Exception as Error:
        logger.error('meet error when saving recent-bad-stock table,Error:{}'.format(Error))

    try:
        PulledUpStocks = is_recent_pulled_up(StocksTable)
        PulledUpStocks.to_csv(WorkPath+'/pulled up stocks.csv',encoding='utf-8-sig')
        logger.success("finish saving pulled-up-stock table")
    except Exception as Error:
        logger.error('meet error when saving pulled-up-stock table,Error:{}'.format(Error))





if __name__ == "__main__":
    main()