import pandas as pd

df = pd.read_csv('BTCUSDT-1m.csv')
data = df.loc[:, ['otime', 'Open', 'Close', 'High', 'Low', 'Volume']]
data[['Open', 'High', 'Low', 'Close', 'Volume']] = data[['Open', 'High', 'Low', 'Close', 'Volume']].astype(
    'float64')
data = data.rename(columns={'otime': 'Date'})
#设置date列为索引，覆盖原来索引,这个时候索引还是 object 类型，就是字符串类型。
data.set_index('Date', inplace=True)
#将object类型转化成 DateIndex 类型，pd.DatetimeIndex 是把某一列进行转换，同时把该列的数据设置为索引 index。
data.index = pd.DatetimeIndex(data.index)
#将时间顺序升序，符合时间序列
data = data.sort_index(ascending=True)

lowList = data['Low'].rolling(9).min() #计算low值9日/分钟移动最低
lowList.fillna(value=data['Low'].expanding().min(), inplace=True)
highList = data['High'].rolling(9).max() #计算high值9日移动最高
highList.fillna(value=data['High'].expanding().max(), inplace=True)
rsv = (data.loc[:, 'Close'] - lowList) / (highList - lowList) * 100
data.loc[:, 'kdj_k'] = rsv.ewm(com=3).mean()
# data.loc[:, 'kdj_d'] = data.loc[:, 'kdj_k'].ewm(com=3).mean()
# data.loc[:, 'kdj_j'] = 3.0 * data.loc[:, 'kdj_k'] - 2.0 * data.loc[:, 'kdj_d']

# print(data)
data.to_excel('kdj_1m.xlsx')