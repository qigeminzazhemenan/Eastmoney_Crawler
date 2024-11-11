from pathlib import Path
from loguru import logger
import pandas as pd
import json
import requests
import re
import time
import datetime 
import os
from urllib.parse import urlencode
from .utils import initalize_logger

#initalize log location
initalize_logger()

#get paths
WorkPath = str(Path(os.path.realpath(__file__)).parent.parent)
DataPath = "{}\\Data".format(WorkPath)

#get date range for kline data based on history record
def get_date_range(TableName) -> dict:
    EndDate = datetime.date.today()
    #if exist hostory data, start from last day recorded
    TablePath = '{}\\{}.json'.format(DataPath,TableName)
    if os.path.exists(TablePath):
        History = pd.read_json(TablePath)
        StartDate = max(History.loc[:,'Date'])
        #start from next day of last day in history
        StartDate += datetime.timedelta(days=1)
    else:
    #if no history data, start from 365 days ago
        Delta = datetime.timedelta(days=365)
        StartDate = EndDate-Delta

    StartDate = str(StartDate).replace('-','')
    EndDate = str(EndDate).replace('-','')

    return StartDate, EndDate



#generate secid
def gen_secid(RawCode: str) -> str:
    '''
    generate Eastmoney secid

    Parameters
    ----------
    rawCode : 6 digit code
    Return
    ------
    str
    '''

    # SSE Composite Index
    if RawCode == '000001':
        return f'1.{RawCode}'
    # Shenzhen Composite Index
    if RawCode == '399106':
        return f'0.{RawCode}'
    # SSE stocks
    if RawCode[0] == '6':
        return f'1.{RawCode}' 
    # Shenzhen stocks
    if RawCode[0] == '0':
        return f'0.{RawCode}'
    


#get kline data
def get_k_history(Code: str, beg: str, end: str, klt: int = 101, adjust: int = 1) -> pd.DataFrame:
    '''
    object: get k-line Data
    -
    params:

        Code : stock secid
        beg: start date like 20200101
        end: end date like 20200201

        klt: interval of k line, default 101 
            klt:1 1 min
            klt:5 5 min
            klt:101 1day
            klt:102 1week
        adjust: stock price adjustment
            adjust:0 no adjustment
            adjust:1 forward stock adjustment
            adjust:2 backward stock adjustment 
    '''  
    EastmoneyHeaders = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; Touch; rv:11.0) like Gecko',
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Referer': 'http://quote.eastmoney.com/center/gridlist.html'}
    
    EastmoneyKlines = {
        'f51': 'Date',
        'f52': 'Open',
        'f53': 'Close',
        'f54': 'Highest',
        'f55': 'Lowest',
        'f56': 'Volume',
        'f57': 'Turnover',
        'f58': 'Price Fluctuation',
        'f59': 'Price Change Rate',
        'f60': 'Price Change',
        'f61': 'Turnover Ratio',
    }
    fields2 = list(EastmoneyKlines.keys())
    fields2 = ",".join(fields2)
    columns = list(EastmoneyKlines.values())
    secid = gen_secid(Code)

    params = (
        ('fields1', 'f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13'),
        ('fields2', fields2),
        ('beg', beg),
        ('end', end),
        ('rtntype', '6'),
        ('secid', secid),
        ('klt', f'{klt}'),
        ('fqt', f'{adjust}'))
    params = dict(params)
    
    #get klines data
    try:
        BaseUrl = 'https://push2his.eastmoney.com/api/qt/stock/kline/get'
        Url = '{}?{}'.format(BaseUrl,urlencode(params))
        JsonResponse: dict = requests.get(Url, headers=EastmoneyHeaders).json()

        #if no data, try changing secid first
        if JsonResponse['data'] is None:
            if secid[0] == '0':
                secid = f'1.{Code}'
            else:
                secid = f'0.{Code}'
            params['secid'] = secid
            Url = BaseUrl+'?'+urlencode(params)
            JsonResponse: dict = requests.get(Url, headers=EastmoneyHeaders).json()      
        
        # check if the stock exists, if do exist, add it into the table
        if JsonResponse['data'] is not None:
            Klines = JsonResponse['data']['klines']
            rows = []
            for Kline in Klines:
                Kline = Kline.split(',')
                rows.append(Kline)  
            result = pd.DataFrame(rows, columns=columns)
   
            #get other features ;ike name, type of industry and Dynamic P/E ratio
            EastmoneyStocks = {
            'f55':'Earnings Per Share',
            'f58':'Trade Type',
            'f127':'Industry Type',
            'f128':'Segment Name',
            'f162': 'P/E Ratio(dynamic)',
            'f163':'P/E Ratio(static)',
            'f167': 'P/B Ratio'
            }
            fields = list(EastmoneyStocks.keys())
            fields = ",".join(fields)
            columns = list(EastmoneyStocks.values())
            secid = gen_secid(Code)

            params = (
            ('fields', fields),
            ('rtntype', '6'),
            ('secid', secid)
            )
            params = dict(params)

            BaseUrl = 'http://push2.eastmoney.com/api/qt/stock/get'
            Url2 = Url = '{}?{}'.format(BaseUrl,urlencode(params))
            JsonResponse2 = requests.get(Url2).json()
            Data2 = JsonResponse2['data']
            StockName = Data2["f58"]
            StockType = Data2["f127"]
            PERatio = Data2["f162"]/100 #in json, there's no '.' in PERatio number, so we use PERatio/100 here 
            result.insert(result.shape[1],'P/E Ratio(dynamic)',PERatio)
            result.insert(0,'Industry Type',StockType)
            result.insert(0,'Stock Name',StockName)
            result.insert(0,'Stock Code',Code)
            return result

    #if error while aquiring a stock 
    except Exception as Error:
        logger.error('meet error when downloading kline info of stock {}, Error:{}'.format(Code,Error))



#get number of foreign holders among top 10(not guaranteed accurate)
def get_foreign_holder_amount(Code: str) ->pd.DataFrame:

    try:
        #get webpage
        BaseUrl = "https://emweb.securities.eastmoney.com/PC_HSF10/ShareholderResearch/Index?type=web&Code="
        Url = BaseUrl+Code
        WebContent = requests.get(Url)

        #select the shareholders section
        HoldersSection = re.findall
        ("注：该图展示了十大流通股东持股、其余流通股份、流通受限股份在总股本中的占比情况，持股比例计算公式为各股份数/总股本。(.+?)</tbody>",
        WebContent,re.S)[0]
        HoldersInfoList = re.findall("<tr>(.+?)</tr>",HoldersSection,re.S)[1:-2]

        #how many ForeignHolders in the top 10
        ForeignHolderAmount = 0

        #if a shareholder is foreign, Amount+=1
        for HolderInfo in HoldersInfoList:
            HolderName = re.findall("<td(.+?)</td>",HolderInfo)[0]
            HolderProperty = re.findall("<td(.+?)</td>",HolderInfo)[1]
            if(HolderName.isalpha() or HolderProperty == "QFII"):
                ForeignHolderAmount += 1

        return ForeignHolderAmount
    
    except Exception as Error:
        logger.error('meet error when downloading info of stock {}, Error:{}'.format(Code,Error))



#update history stock table (or create one if not exist)
def update_stock_table(TableName:str, Codes:list, klt: int = 101, adjust: int = 1):
    StartTime = time.time()

    StartDate, EndDate = get_date_range(TableName)
    KLines = pd.DataFrame()
    for Code in Codes:
        print(f'fetching kline data of: {Code} ')
        KLineNew = get_k_history(Code, StartDate, EndDate)
        KLines = pd.concat([KLines,KLineNew],ignore_index=True)

    #TablePath = "{}\\{}.json".format(DataPath,TableName)
    TablePath = "{}\\{}.csv".format(DataPath,TableName)
    if os.path.exists(TablePath):
        History = pd.read_csv(TablePath,encoding='gbk')
        KLines = pd.concat([KLines,History],ignore_index=True)
    
    #adjust format
    KLines.sort_values(by=['Stock Code','Date'],inplace=True)

    try:
        #KLines.to_json(TablePath,date_format='iso',orient='records')
        KLines.to_csv(TablePath,index=False,encoding='gbk')
        EndTime = time.time()
        ElapsedTime = (StartTime-EndTime)/60
        logger.success('finish saving table {}.csv, time spent:{}minutes'.format(TableName,ElapsedTime))
    except Exception as Error:
        logger.error('meet error when saving table {}.csv,Error:{}'.format(TableName,Error))

    StockCodesPath = "{}\\{}_codes.json".format(DataPath,TableName)
    if not os.path.exists(StockCodesPath):
        try:
            with open(StockCodesPath,'w') as File:
                StockCodes = [str(i) for i in set(KLines.loc[:,'Stock Code'])]
                StockCodes.sort()
                json.dump(StockCodes,File)
        except Exception as Error:
            logger.error('meet error when saving Codes.json: {},Error:{}'.format(TableName,Error))


