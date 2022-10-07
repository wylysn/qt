import pandas as pd
import mplfinance as mpf
from pylab import mpl
import numpy as np

df = pd.read_csv('ETHUSDT-5m.csv')

df.sort_values(by='otime',ascending=True)
data1 = df.iloc[0:49]
data1 = data1.rename(columns={'Open time': 'Opentime'})

data = data1.loc[:, ['Opentime', 'otime', 'Open', 'Close', 'High', 'Low', 'Volume']]
data = data.rename(columns={'otime': 'Date'})  #更换列名，为后面函数变量做准备

x = [12,43]
y = [3382.22,3408.78]
z1 = np.polyfit(x, y, 1)
print(z1)
yvals=np.polyval(z1,12)
print(yvals)

data['nc'] = np.polyval(z1,data.index)
print(data)
#设置date列为索引，覆盖原来索引,这个时候索引还是 object 类型，就是字符串类型。
data.set_index('Date', inplace=True)
#将object类型转化成 DateIndex 类型，pd.DatetimeIndex 是把某一列进行转换，同时把该列的数据设置为索引 index。
data.index = pd.DatetimeIndex(data.index)

# print(data)

#将时间顺序升序，符合时间序列
data = data.sort_index(ascending=True)

mpl.rcParams['font.sans-serif'] = ['SimHei']  # 指定默认字体
mpl.rcParams["figure.figsize"] = [6.4, 4.8]
mpl.rcParams['axes.unicode_minus'] = False  # 解决保存图像是负号'-'显示为方块的问题
apdict = mpf.make_addplot(data['nc'])
mpf.plot(data, type='candle', mav=(5, 10, 20), volume=True,addplot=apdict, show_nontrading=False)

