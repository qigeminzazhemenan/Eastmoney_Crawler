import sys
import os
from pathlib import Path
import pandas as pd
import datetime 
import re
import traceback
from loguru import logger
from Modules import *

#---
def main():
    
    WorkPath = str(Path(os.path.realpath(__file__)).parent)
    ModulePath = "{}\\Modules".format(WorkPath)
    DataPath = "{}\\Data".format(WorkPath)
    ResultPath = "{}\\Data\\Result".format(WorkPath)

    sys.path.append(ModulePath)

    #log dir
    logger.add('{}\\{}'.format(WorkPath,'log.log'), rotation="1 MB")

    #get SSE Composite-----
    TableName = 'SSE'
    SSECode = ['000001']
    update_stock_table(TableName=TableName, Codes=SSECode)

    #get SSE Stocks ------
    # list of stock codes
    TableName = 'SH_stocks'
    StockCodesPath = "{}\\{}_codes.json".format(DataPath,TableName)
    if os.path.exists(StockCodesPath):
        with open(StockCodesPath) as File:
            SHCodes = list(json.load(File))
    else:
        SHCodes = [str(i) for i in range(600000,609000)]
    #used for debug
    #SHCodes = [str(600000),str(600004)]
    
    #write into stock table
    #update_stock_table(TableName=TableName, Codes=SHCodes)
    
    #------
    
    #analysis
    Table = '{}\\{}.csv'.format(DataPath,TableName)
    Table = pd.read_csv(Table,encoding='gbk')
    try:
        GoodStocks = is_recent_good(Table)  
        GoodStocks.to_csv('{}\\good_stocks.csv'.format(ResultPath),encoding='gbk')
        logger.success("finish saving recent-good-stock table")
    except Exception as Error:   
        logger.error('meet error when saving recent-good-stock table,Error:{}, traceback:{}'.format(Error,traceback.format_exc()))

    try:
        BadStocks = is_recent_bad(Table) 
        BadStocks.to_csv('{}\\bad_stocks.csv'.format(ResultPath),encoding='gbk')
        logger.success("finish saving recent-bad-stock table")
    except Exception as Error:
        logger.error('meet error when saving recent-bad-stock table,Error:{}'.format(Error))

    try:
        PulledUpStocks = is_recent_pulled_up(Table)
        PulledUpStocks.to_csv('{}\\pulled_up_stocks.csv'.format(ResultPath),encoding='gbk')
        logger.success("finish saving pulled-up-stock table")
    except Exception as Error:
        logger.error('meet error when saving pulled-up-stock table,Error:{}'.format(Error))





if __name__ == "__main__":
    main()