import pandas as pd
import numpy as np
from datetime import datetime, timedelta

start_date = datetime.strptime('2022-09-15 08:00:00', '%Y-%m-%d %H:%M:%S')
print(start_date+timedelta(minutes=-1))

# df = pd.DataFrame(columns=['buytime','buycount','buyprice'])
# final_date2 = datetime.strptime('2022-9-30 10:38:00', '%Y-%m-%d %H:%M:%S')
# df.loc[len(df)] = [final_date2, 3, 4]
# df.loc[len(df)] = [final_date2, 1, 8]
# df2 = df.max()
# print(df2['buyprice'])
# #设置date列为索引，覆盖原来索引,这个时候索引还是 object 类型，就是字符串类型。
# df.set_index('buytime', inplace=True)
# #将object类型转化成 DateIndex 类型，pd.DatetimeIndex 是把某一列进行转换，同时把该列的数据设置为索引 index。
# df.index = pd.DatetimeIndex(df.index)
# #将时间顺序升序，符合时间序列
# data = df.sort_index(ascending=True)
# print(df.loc[final_date2, 'buycount'])
# print(df.loc[0]['buycount'])
# buycount = df['buycount'].sum()
# buyprice = df['buyprice'].sum()
# df=df.drop(index=df.index)
# print(df)

# ac = Account(100000, 0.1, None, None)
# ac.printinfo()

# ac = Account(1000000, 10000, 0.1, None, None)
# ac.buy(final_date2, 1, 1, 1000, 10000)

from matplotlib import pyplot as plt
# print(1+(1495.4144999444966-1511.864059443886)/1495.4144999444966)
# print(677.6338206959542 * 1495.4144999444966)
# print(677.6338206959542 * 1474.841133 * (1+(1474.841133-1511.864059443886)/1474.841133))
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

# df = pd.read_excel('/Users/wangyilu/PycharmProjects/qt/MA60/rate_yield.xlsx')
# X = df['closetime']
# Y = df['allmoney']
# x_data = np.array(df['closetime'],type(datetime))
# y_data = np.array(df['allmoney'],type(float))
# plt.plot(x_data, y_data, color='red')
# plt.xlabel('time')
# plt.ylabel('rate')
# plt.show()

# df = pd.DataFrame({'A': 'foo bar foo bar foo bar foo foo'.split(),
#                    'B': 'one one two three two two one three'.split(),
#                    'C': np.arange(8), 'D': np.arange(8) * 2})
# print(df)
#      A      B  C   D
# 0  foo    one  0   0
# 1  bar    one  1   2
# 2  foo    two  2   4
# 3  bar  three  3   6
# 4  foo    two  4   8
# 5  bar    two  5  10
# 6  foo    one  6  12
# 7  foo  three  7  14
# print(df.loc[df['A'] == 'foo'])
# #如果要包含多个值，请将它们放在列表中，并使用isin：
# print(df.loc[df['B'].isin(['one','three'])])
# #如果希望多次执行此操作，则先创建索引然后再使用df.loc会更高效：
# df = df.set_index(['B'])
# print(df.loc['one'])
# #或者，要包含多个值，可以使用df.index.isin：
# print(df.loc[df.index.isin(['one','two'])])
# a = 'one'
# print(a)
# print(df.loc[0]['B'])
# print(df.loc[df['A'] == 'bar'].tail(1).iloc[0]['B'])
# b = df.loc[df['A'] == 'bar'].tail(2)
#
# print(2**4)
