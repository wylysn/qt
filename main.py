import pandas as pd
from datetime import datetime, time, timedelta
import globalConf
import talib

from FutureAccount import FutureAccount

global log
log = globalConf.getShareLogger()

data = pd.read_csv('/Users/wangyilu/PycharmProjects/qt/ETHUSDT/ETHUSDT-1m_time.csv')
data = data.loc[:, ['Open time', 'Open', 'Close', 'High', 'Low']]
# data['starttime'] = pd.to_datetime(data['Open time'])
#设置date列为索引，覆盖原来索引,这个时候索引还是 object 类型，就是字符串类型。
data.set_index('Open time', inplace=True)
#将object类型转化成 DateIndex 类型，pd.DatetimeIndex 是把某一列进行转换，同时把该列的数据设置为索引 index。
data.index = pd.DatetimeIndex(data.index)
#将时间顺序升序，符合时间序列
data = data.sort_index(ascending=True)
df_1d = data
df_1d = df_1d.resample('D').agg({'Open':'first','Close':'last','High':'max','Low':'min'})
df_1d['preClose'] = df_1d['Close'].shift(1)
df_1d['preHigh'] = df_1d['High'].shift(1)
df_1d['preLow'] = df_1d['Low'].shift(1)
df_1d['upperline'] = df_1d['High'].rolling(window=20).max()
df_1d['lowline'] = df_1d['Low'].rolling(window=20).min()
df_1d['middleline'] = df_1d[['upperline', 'lowline']].apply(lambda x: (x['upperline'] + x['lowline']) / 2, axis=1)

df_1d['TR'] = df_1d[['High', 'Low', 'Close', 'preHigh', 'preLow', 'preClose']].apply(
    lambda x: max(x['High'] - x['Low'], x['preHigh'] - x['preClose'], x['preClose'] - x['preLow']),
    axis=1)
# 计算 ATR 值
df_1d['ATR5'] = df_1d['TR'].rolling(window=5).mean()
df_1d['ATR20'] = df_1d['TR'].rolling(window=20).mean()

df_1d['SAR'] = talib.SAR(df_1d['High'].values, df_1d['Low'].values, acceleration=0.02)
df_1d.to_excel('eth_calc.xlsx', index=True)
