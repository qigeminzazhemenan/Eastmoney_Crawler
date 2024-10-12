from urllib import request
from urllib.parse import urlencode
import numpy as np
import pandas as pd
import requests
import re
from loguru import logger

#log dir
logger.add("file_1.log", rotation="1 MB")

#生成东方财富专用的secid
def gen_secid(rawC: str) -> str:
    '''
    生成东方财富专用的secid

    Parameters
    ----------
    rawC : 6 位股票代码

    Return
    ------
    str: 指定格式的字符串

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
    # 深市股票
    else:
        return f'1.{rawC}'
    
#获取k线数据
def get_k_history(Code: str, beg: str, end: str, klt: int = 101, fqt: int = 2) -> pd.DataFrame:
    '''
    object: get k-line Data
    -
    params:

        Code : 6 位股票代码
        beg: 开始日期 例如 20200101
        end: 结束日期 例如 20200201

        klt: k线间距 默认为 101 即日k
            klt:1 1 分钟
            klt:5 5 分钟
            klt:101 日
            klt:102 周
        fqt: 复权方式
            不复权 : 0
            前复权 : 1
            后复权 : 2 
    '''
    EastmoneyKlines = {
        'f51': '日期',
        'f52': '开盘',
        'f53': '收盘',
        'f54': '最高',
        'f55': '最低',
        'f56': '成交量',
        'f57': '成交额',
        'f58': '振幅',
        'f59': '涨跌幅',
        'f60': '涨跌额',
        'f61': '换手率',
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
        ('fqt', f'{fqt}'))
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
                'f55':'每股收益',
                'f58':'交易类型',
                'f127':'行业类型',
                'f128':'板块名称',
                'f162': '动态市盈率',
                'f163':'静态市盈率',
                'f167': '市净率'
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
                result.insert(0,'股票代码',Code)
            
            return result

    #if error while aquiring a stock 
    except Exception as Error:
        logger.add('meet error when downloading info of stock {}, Error:{}'.format(Code,Error))



#get number of foreign holder 
# s among top 10(not guaranteed accurate)
def get_foreign_holder_amount(Code: str) ->pd.DataFrame:
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
    
    