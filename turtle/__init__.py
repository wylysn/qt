import pandas as pd
from datetime import datetime, timedelta
from Account import Account
from logbook import Logger
import logbook
import globalConf
global log
log = globalConf.getShareLogger()

df = pd.read_csv('BTCUSDT-1m-latest10.csv')
data = df.loc[:, ['otime', 'Open', 'Close', 'High', 'Low', 'Volume']]
data = data.rename(columns={'otime': 'Date'})
#设置date列为索引，覆盖原来索引,这个时候索引还是 object 类型，就是字符串类型。
data.set_index('Date', inplace=True)
#将object类型转化成 DateIndex 类型，pd.DatetimeIndex 是把某一列进行转换，同时把该列的数据设置为索引 index。
data.index = pd.DatetimeIndex(data.index)
#将时间顺序升序，符合时间序列
data = data.sort_index(ascending=True)

# for test
# t_date = datetime.strptime('2020-11-30 14:00:00', '%Y-%m-%d %H:%M:%S')
# data.loc[t_date, ['High', 'Low']]
# t1_date = t_date + timedelta(minutes=1)

#最开始10天行情
s_date = datetime.strptime('2022-09-15 08:00:00', '%Y-%m-%d %H:%M:%S')
e_date = datetime.strptime('2022-09-25 07:59:00', '%Y-%m-%d %H:%M:%S')
final_date = datetime.strptime('2022-10-05 07:59:00', '%Y-%m-%d %H:%M:%S')

# test_date = datetime.strptime('2020-11-29 14:00:00', '%Y-%m-%d %H:%M:%S')
# if test_date in data.index.values:
#     print(df.loc[test_date])
# else:
#     print('None')

# all_money = 1000000
# buy_money = 0
# sell_money = 0
# stop_profit = 0.1
# buy_type = None    # 0:做多；1:做空
# buy_records = pd.DataFrame(columns=['buytime', 'buycount', 'buyprice'])
ac = Account(1000000, 1000000, 0.01, None, None)
max_profit = 0
qt_start_time = e_date + timedelta(minutes=1)

n_loc = data.loc[qt_start_time, ['High', 'Low']]
while True:
    log.info('--------------------------------')
    log.info('当前时间：' + str(qt_start_time))

    if n_loc is not None:
        perioddata = data.loc[s_date:e_date]    #入场1数据集（10天数据）
        # 求最大值、最小值
        maxdf = perioddata.max()
        mindf = perioddata.min()
        maxprice = maxdf['High']
        minprice = mindf['Low']
        log.info('前10天最高价格：' + str(maxprice) + ';最低价格：' + str(minprice))

        current9 = qt_start_time.replace(qt_start_time.year, qt_start_time.month, qt_start_time.day, 9, 0, 0)
        current11 = qt_start_time.replace(qt_start_time.year, qt_start_time.month, qt_start_time.day, 11, 0, 0)
        if qt_start_time < current11:
            current9 = current9 - timedelta(hours=24)
            current11 = current11 - timedelta(hours=24)
        log.info('前一个11点：' + str(current11))
        twohours_data = data.loc[current9:current11]
        twohours_maxdf = perioddata.max()
        twohours_mindf = perioddata.min()
        twohours_maxprice = maxdf['High']
        twohours_minprice = mindf['Low']
        twohours_gapprice = twohours_maxprice - twohours_minprice
        log.info('2小时内价差：' + str(twohours_maxprice) + '-' + str(twohours_minprice) + '=' + str(twohours_gapprice))

        n_maxprice = n_loc['High']
        n_minprice = n_loc['Low']
        log.info('当前最高价格：' + str(n_maxprice) + ';最低价格：' + str(n_minprice))

        # 进场1判断
        if n_maxprice > maxprice or n_minprice < minprice:
            if n_maxprice > maxprice and ac.buy_type is None:
                # ac.buy(qt_start_time, 1, 1, maxprice, ac.unit)
                ac.buy(qt_start_time, 1, 1, maxprice, ac.all_money) #全仓买入
            elif n_minprice < minprice and ac.buy_type is None:
                # ac.buy(qt_start_time, 1, 2, maxprice, ac.unit)
                ac.buy(qt_start_time, 1, 2, maxprice, ac.all_money) #全仓买入
        # 进场2判断
        if n_maxprice > twohours_maxprice + twohours_gapprice or n_minprice < twohours_minprice - twohours_gapprice:
            # if n_maxprice > twohours_maxprice + twohours_gapprice and ac.buy_type is None:
            if n_maxprice > twohours_maxprice + twohours_gapprice:
                # ac.buy(qt_start_time, 2, 1, twohours_maxprice + twohours_gapprice, ac.unit)
                ac.buy(qt_start_time, 2, 1, twohours_maxprice + twohours_gapprice, ac.all_money)    #全仓买入
            elif n_minprice < twohours_minprice - twohours_gapprice:
                # ac.buy(qt_start_time, 2, 2, twohours_minprice - twohours_gapprice, ac.unit)
                ac.buy(qt_start_time, 2, 2, twohours_minprice - twohours_gapprice, ac.all_money)

        if len(ac.buy_records) > 0:
            ac.avg_price = ac.buy_records['buymoney'].sum() / ac.buy_records['buycount'].sum()

            # 止损出场
            if ac.buy_type == 1 and n_minprice <= ac.avg_price * (1 - ac.stop_profit):
                ac.sell(qt_start_time, 1, ac.avg_price * (1 - ac.stop_profit))
                sell_completed_flag = 1
            elif ac.buy_type == 2 and n_maxprice >= ac.avg_price * (1 + ac.stop_profit):
                ac.sell(qt_start_time, 1, ac.avg_price * (1 + ac.stop_profit))
                sell_completed_flag = 1

            # 获利回调出场
            if sell_completed_flag != 1:
                if ac.buy_type == 1 or ac.buy_type == 2:
                    if ac.buy_type == 1:
                        profit = (n_maxprice-ac.avg_price)/ac.avg_price
                    if ac.buy_type == 2:
                        profit = (ac.avg_price-n_minprice)/ac.avg_price
                if max_profit < profit:
                    max_profit = profit
                if max_profit > 0 and profit <= max_profit*0.75:
                    if ac.buy_type == 1:
                        price = ac.avg_price * (1 + max_profit * 0.75)
                    if ac.buy_type == 2:
                        price = ac.avg_price * (1 - max_profit * 0.75)
                    ac.sell(qt_start_time, 2, price)
                    max_profit = 0

    sell_completed_flag = 0
    s_date = s_date + timedelta(minutes=1)
    e_date = e_date + timedelta(minutes=1)
    qt_start_time = e_date + timedelta(minutes=1)

    try:
        n_loc = data.loc[qt_start_time, ['High', 'Low']]
    except:
        n_loc = None

    if qt_start_time > final_date:
        if len(ac.buy_records)>0:
            ac.avg_price = ac.buy_records['buymoney'].sum() / ac.buy_records['buycount'].sum()
            buycount = ac.buy_records['buycount'].sum()
            log.info('最后有这么多钱：' + str(ac.all_money + ac.avg_price * buycount))
        else:
            log.info('最后有这么多钱：' + str(ac.all_money))
        break

