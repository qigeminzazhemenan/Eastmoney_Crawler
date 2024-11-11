import numpy as np
import pandas as pd


#A is the stock, B is the Market 
def beta_cofficient(DataA,DataB):return np.cov(DataA,DataB)/np.var(DataB)


def is_recent_pulled_up(Table,Recent=5,ExceptDays=1):
    '''
    check if the stock is recently pulled up

    Table: the stock table excel
    Recent: Number of recent days 
    ExceptDays: sometimes in the pull-up process, there may be one or more days of exception(price not going up much),
                ExceptDays is the number of days allowed for such exception
    '''
    def is_pulled_up(Open,Close,Rate):
        Mask1 = ((Close-Open)/Open)<0.05
        Mask2 = Rate>0.1
        Mask = pd.concat([Mask1,Mask2],axis=1).all(axis=1)
        return Mask

    KLines = pd.read_excel(Table,sheet_name='Sheet1')
    Open = KLines.loc[:,'开盘']
    Close = KLines.loc[:,'收盘']
    Rate = KLines.loc[:,'涨跌幅']
    KLines['当日拉升迹象'] = is_pulled_up(Open,Close,Rate)
    Groups =KLines.groupby(['股票代码',"股票名称"])

    Grpby = Groups.agg({'当日拉升迹象':[('近期总拉升天数',lambda x: np.sum(x.iloc[-Recent:]) )]})
    Mask = Grpby.loc[:,'当日拉升迹象']['近期总拉升天数'] >=Recent-ExceptDays

    PulledUpStocks = Grpby.loc[Mask].index
    PulledUpStocksIndex = Grpby.loc[Mask].index
    PulledUpStocks = []
    for Stock in GoodStocksIndex:GoodStocks.append(Stock)
    GoodStocks = pd.DataFrame(GoodStocks)    
    return GoodStocks
    return PulledUpStocks


def is_recent_good(Table,Recent=5,Days=90):
    '''
    check if the stock is recently on the better way

    Table: the stock table excel
    Recent: what is 'recent days' (default since 5 days ago)
    Days: length of days for comparison with Recent
    '''

    KLines = pd.read_excel(Table,sheet_name='Sheet1')
    Groups =KLines.groupby(['股票代码',"股票名称"])
    
    #filter
    def CoV_first(Data,Cut,Days):return (np.var(Data.iloc[-Days:-Cut],ddof=1))**0.5/np.mean(Data.iloc[-Days:-Cut]) 
    def min_last(Data,Cut):return np.min(Data.iloc[-Cut:]) 
    def max_last(Data,Cut):return np.max(Data.iloc[-Cut:])  
    def mean_last(Data,Cut):return np.mean(Data.iloc[-Cut:]) 

    Grpby = Groups.agg({'收盘':[('前变异系数',lambda x: CoV_first(Data=x,Cut=Recent,Days=Days) )],
                              '涨跌幅':[('后最小',lambda x: min_last(Data=x,Cut=Recent) ),
                              ('后最大',lambda x: max_last(Data=x,Cut=Recent) ),
                              ('后平均',lambda x: mean_last(Data=x,Cut=Recent) )],
                              '换手率':[('后平均',lambda x: mean_last(Data=x,Cut=Recent) )]})


    Mask1 = abs(Grpby.loc[:,'收盘']['前变异系数']) > 0.1
    Mask2 = Grpby.loc[:,'涨跌幅']['后最小'] > -2
    Mask3 = Grpby.loc[:,'涨跌幅']['后最大'] < 10
    Mask4 = Grpby.loc[:,'涨跌幅']['后平均'] > 3
    Mask5 = Grpby.loc[:,'换手率']['后平均'] > 2
    Mask = pd.concat([Mask1,Mask2,Mask3,Mask4,Mask5],axis=1).all(axis=1)

    GoodStocksIndex = Grpby.loc[Mask].index
    GoodStocks = []
    for Stock in GoodStocksIndex:GoodStocks.append(Stock)
    GoodStocks = pd.DataFrame(GoodStocks)    
    return GoodStocks


def is_recent_bad(Table,Recent=5,Days=90):
    '''
    check if the stock is recently on the worse way

    Table: the stock table excel
    Recent: what is 'recent days' (default since 5 days ago)
    Days: number of recent days used for comparison 
    '''

    KLines = pd.read_excel(Table,sheet_name='Sheet1')
    Groups =KLines.groupby(['股票代码',"股票名称"])

    #filters
    def CoV_last(Data,Cut):return (np.var(Data.iloc[-Cut:],ddof=1))**0.5/np.mean(Data.iloc[-Cut:]) 
    def min_last(Data,Cut):return np.min(Data.iloc[-Cut:]) 
    def max_last(Data,Cut):return np.max(Data.iloc[-Cut:])  
    def mean_last(Data,Cut):return np.mean(Data.iloc[-Cut:]) 
    def decrease_rate(Data,Cut,Days):return((np.mean(Data.iloc[-Days:-Cut])-np.mean(Data.iloc[-Cut:]))/np.mean(Data.iloc[-Cut:]))
    Grpby = Groups.agg({'收盘':[('后变异系数',lambda x: CoV_last(Data=x,Cut=Recent) ),
                              ('下降比率',lambda x: decrease_rate(Data=x,Cut=Recent,Days=Days) )],
                              '涨跌幅':[('后最小',lambda x: min_last(Data=x,Cut=Recent) ),
                              ('后最大',lambda x: max_last(Data=x,Cut=Recent) ),
                              ('后平均',lambda x: mean_last(Data=x,Cut=Recent) )],
                              '换手率':[('后平均',lambda x: mean_last(Data=x,Cut=Recent) )]})

    Mask1 = Grpby.loc[:,'收盘']['下降比率'] > 5
    Mask2 = abs(Grpby.loc[:,'收盘']['后变异系数']) < 0.2#0.2
    Mask3 = Grpby.loc[:,'涨跌幅']['后最小'] > -4
    Mask4 = Grpby.loc[:,'涨跌幅']['后最大'] < 4
    Mask5 = Grpby.loc[:,'涨跌幅']['后平均'] < 1
    Mask = pd.concat([Mask1,Mask2,Mask3,Mask4,Mask5],axis=1).all(axis=1)

    BadStocksIndex = Grpby.loc[Mask].index
    BadStocks = []
    for Stock in BadStocksIndex:BadStocks.append(Stock)
    BadStocks = pd.DataFrame(BadStocks)  
    return BadStocks
   



 
