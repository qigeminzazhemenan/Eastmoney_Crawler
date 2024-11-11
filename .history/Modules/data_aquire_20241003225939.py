#from urllib import request
from urllib.parse import urlencode
#import numpy as np
import pandas as pd
import requests
import re
from loguru import logger

#log dir
logger.add("file_1.log", rotation="1 MB")

#生成东方财富专用的secid
def gen_secid(rawC: str) -> str:
    '''
    generate Eastmoney secid

    Parameters
    ----------
    rawC : 6 digit code
    Return
    ------
    str

    '''
    # SSE Composite Index
    if rawC[:3] == '000':
        return f'1.{rawC}'
    # Shenzhen Index
    elif rawC[:3] == '399':
        return f'0.{rawC}'
    # SSE stocks
    elif rawC[0] != '6':
        return f'0.{rawC}'
    # Shenzhen stocks
    else:
        return f'1.{rawC}'
    
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
    EastmoneyKlines = {
        'f51': 'Date',
        'f52': 'Open',
        'f53': 'Close',
        'f54': 'Highest',
        'f55': 'Lowest',
        'f56': 'Volume',
        'f57': ' Turnover',
        'f58': 'Price Fluctuation',
        'f59': 'Price Change Rate',
        'f60': 'Price Change',
        'f61': 'Turnover Ratio',
    }
    
    EastmoneyHeaders = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; Touch; rv:11.0) like Gecko',
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Referer': 'http://quote.eastmoney.com/center/gridlist.html'}
    
    fields = list(EastmoneyKlines.keys())
    columns = list(EastmoneyKlines.values())
    fields2 = ",".join(fields)
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
        Url = BaseUrl+'?'+urlencode(params)
        JsonResponse: dict = requests.get(Url, headers=EastmoneyHeaders).json()

        if JsonResponse['data'] is None:
            if secid[0] == '0':
                secid = f'1.{Code}'
            else:
                secid = f'0.{Code}'
            params['secid'] = secid
            Url = BaseUrl+'?'+urlencode(params)
            JsonResponse: dict = requests.get(Url, headers=EastmoneyHeaders).json()      
        
        # check if the stock exists, if do exist, add it into the table
        if not(JsonResponse['data'] is None):
            Klines = JsonResponse['data']['klines']
            rows = []
            for Kline in Klines:
                Kline = Kline.split(',')
                rows.append(Kline)  
            result = pd.DataFrame(rows, columns=columns)

            # if is stock, get its name, type of industry and Dynamic P/E ratio
            if not(Code[:3] == '000'):

                EastmoneyOtherInfo = {
                'f55':'Earnings Per Share',
                'f58':'Trade Type',
                'f127':'Industry Type',
                'f128':'Segment Name',
                'f162': 'P/E Ratio(dynamic)',
                'f163':'P/E Ratio(static)',
                'f167': 'P/B Ratio'
                }
                Url2 = 'http://push2.eastmoney.com/api/qt/stock/get?fields=f58,f127,f162&secid=1.'+Code
                JsonResponse2 = requests.get(Url2).json()
                Data2 = JsonResponse2['data']
                StockName = Data2["f58"]
                StockType = Data2["f127"]

                #in json, there's no '.' in PERatio number, so we use PERatio/100 here 
                PERatio = Data2["f162"]/100

                result.insert(result.shape[1],'动态市盈率（昨日）',PERatio)
                result.insert(0,'行业类型',StockType)
                result.insert(0,'股票名称',StockName)
                result.insert(0,'code',Code)
            
            return result

    #if error while aquiring a stock 
    except Exception as Error:
        logger.add('meet error when downloading info of stock {}, Error:{}'.format(Code,Error))



#get number of foreign holder 
# s among top 10(not guaranteed accurate)
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
        logger.add('meet error when downloading info of stock {}, Error:{}'.format(Code,Error))
    
    