import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from Account import Account

# df = pd.DataFrame(columns=['buytime','buycount','buyprice'])
# final_date2 = datetime.strptime('2022-9-30 10:38:00', '%Y-%m-%d %H:%M:%S')
# df.loc[len(df)] = [final_date2, 3, 4]
# # df.loc[len(df)] = [final_date2, 1, 8]
# #设置date列为索引，覆盖原来索引,这个时候索引还是 object 类型，就是字符串类型。
# df.set_index('buytime', inplace=True)
# #将object类型转化成 DateIndex 类型，pd.DatetimeIndex 是把某一列进行转换，同时把该列的数据设置为索引 index。
# df.index = pd.DatetimeIndex(df.index)
# #将时间顺序升序，符合时间序列
# data = df.sort_index(ascending=True)
# print(df.loc[final_date2, 'buycount'])
# print(df.loc[0])
# buycount = df['buycount'].sum()
# buyprice = df['buyprice'].sum()
# df=df.drop(index=df.index)
# print(df)

# ac = Account(100000, 0.1, None, None)
# ac.printinfo()

# ac = Account(1000000, 10000, 0.1, None, None)
# ac.buy(final_date2, 1, 1, 1000, 10000)

from matplotlib import pyplot as plt

# rs = pd.DataFrame(columns=['closetime', 'allmoney'])
# c1time = datetime.strptime('2022-9-01', '%Y-%m-%d')
# c2time = datetime.strptime('2022-9-02', '%Y-%m-%d')
# c3time = datetime.strptime('2022-9-03', '%Y-%m-%d')
# c1money = 0.1
# c2money = 0.2
# c3money = 0.15
# rs.loc[len(rs)] = [c1time, c1money]
# rs.loc[len(rs)] = [c2time, c2money]
# rs.loc[len(rs)] = [c3time, c3money]
# x_data = np.array(rs['closetime'],type(datetime))
# y_data = np.array(rs['allmoney'],type(float))
# plt.plot(x_data, y_data, color='red')
# plt.xlabel('time')
# plt.ylabel('rate')
# plt.show()

df = pd.read_excel('rate_yield.xlsx')
X = df['closetime']
Y = df['allmoney']
x_data = np.array(df['closetime'],type(datetime))
y_data = np.array(df['allmoney'],type(float))
plt.plot(x_data, y_data, color='red')
plt.xlabel('time')
plt.ylabel('rate')
plt.show()