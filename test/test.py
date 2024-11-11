
import sys
import os
from pathlib import Path
from urllib import request
from urllib.parse import urlencode
import numpy as np
import pandas as pd
import requests
import datetime 
import re
import time
import json
from sqlalchemy import create_engine
import urllib
DataPath = str(Path(os.path.realpath(__file__)).parent.parent)+'\\Data'
TablePath = DataPath+'\\SSE.json'
History = pd.read_json(TablePath)

import pandas as pd

# Example DataFrame with datetime values
df = pd.DataFrame({
    'datetime': [pd.to_datetime('2024-11-08 15:30:45'), pd.to_datetime('2024-10-05 08:10:20')]
})

# Check the DataFrame structure
print(df)

# Extract only the date part from the 'datetime' column
df['date'] = df['datetime'].dt.date

# Convert the DataFrame to JSON, with the 'date' column
json_str = df[['date']].to_json(date_format='iso', orient='records')
print(json_str)
'''
username = 'root'  # Replace with your MySQL username
password = 'Maroon@Navy1'  # Replace with your MySQL password
password = urllib.parse.quote(password)
host = 'localhost'           # Replace with your host if different
database = 'test'         # The database you created

# Create an SQLAlchemy engine
engine = create_engine(f'mysql+mysqlconnector://{username}:{password}@{host}/{database}')
print(engine)
try:
    with engine.connect() as connection:
        print("Connection to the MySQL database was successful!")
except Exception as e:
    print("Failed to connect to the MySQL database.")
    print("Error details:", e)
History.to_sql('SSE', con=engine, if_exists='replace', index=False)
result_df = pd.read_sql('SELECT * FROM sse', con=engine)
print(result_df)






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

file = '20240806.xlsx'
base = os.path.splitext(file)[0]
os.rename(file,base + '.csv')
'''