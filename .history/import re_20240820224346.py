
import sys
import os
from urllib import request
from urllib.parse import urlencode
import numpy as np
import pandas as pd
import requests
import datetime 
import re
import time
'''
WorkPath = os.getcwd()
ModulePath = WorkPath+"\\Modules"
sys.path.append(ModulePath)
from feature_functions import *
from data_aquire import *
from others import *

def get_foreign_holder_amount(code: str) -> int:
    #get webpage content
    BaseUrl = "https://emweb.securities.eastmoney.com/PC_HSF10/ShareholderResearch/Index?type=web&code=sh"
    Url = BaseUrl+code
    EastmoneyHeaders = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; Touch; rv:11.0) like Gecko',
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Referer': 'https://quote.eastmoney.com/sh'+code+'.html'}
    WebAnswer = requests.get(Url,EastmoneyHeaders)
    WebAnswer.encoding = WebAnswer.apparent_encoding
    WebContent = WebAnswer.text
    #select the shareholders section
    HoldersSection = re.findall("注：该图展示了十大流通股东持股(.+?)</tbody>",WebContent,re.S)[0]
    print(type(HoldersSection))
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
    
#print(get_foreign_holder_amount("600602"))


get_k_history("600013", "20240122", "20240125")
'''
file = '20240806.xlsx'
base = os.path.splitext(my_file)[0]
os.rename(my_file, base + '.bin')