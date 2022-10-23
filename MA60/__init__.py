import pandas as pd
from datetime import datetime, timedelta
from Account import Account
from logbook import Logger
import logbook
import globalConf
global log
log = globalConf.getShareLogger()

data = pd.read_csv('/Users/wangyilu/PycharmProjects/qt/BTCUSDT/BTCUSDT-1m-latest10.csv')
# data = pd.read_csv('/Users/wangyilu/PycharmProjects/qt/BTCUSDT/BTCUSDT-1m.csv')
# data = pd.read_csv('BTCUSDT-1m.csv')
data = data.loc[:, ['otime', 'Open', 'Close', 'High', 'Low', 'Volume']]
data = data.rename(columns={'otime': 'Date'})
#设置date列为索引，覆盖原来索引,这个时候索引还是 object 类型，就是字符串类型。
data.set_index('Date', inplace=True)
#将object类型转化成 DateIndex 类型，pd.DatetimeIndex 是把某一列进行转换，同时把该列的数据设置为索引 index。
data.index = pd.DatetimeIndex(data.index)
#将时间顺序升序，符合时间序列
data = data.sort_index(ascending=True)

# 计算60、600分钟的close平均线
ma60List = data['Close'].rolling(60).mean()
data.loc[:, 'MA60'] = ma60List
ma600List = data['Close'].rolling(1440).mean()
data.loc[:, 'MA600'] = ma600List

data.to_excel('MA60-600.xlsx')

start_date = datetime.strptime('2022-09-15 08:00:00', '%Y-%m-%d %H:%M:%S')
final_date = datetime.strptime('2022-10-05 07:59:00', '%Y-%m-%d %H:%M:%S')
# start_date = datetime.strptime('2021-10-01 08:00:00', '%Y-%m-%d %H:%M:%S')
# final_date = datetime.strptime('2022-10-01 07:59:00', '%Y-%m-%d %H:%M:%S')

ac = Account(1000000, 100000, 0.01, None, None)
max_profit = 0
qt_start_time = start_date + timedelta(minutes=1440)

n_loc = data.loc[qt_start_time, ['Open', 'High', 'Low']]

while True:
    log.info('--------------------------------')
    log.info('当前时间：' + str(qt_start_time))

    if n_loc is not None:
        n_maxprice = n_loc['High']
        n_minprice = n_loc['Low']
        log.info('当前最高价格：' + str(n_maxprice) + ';最低价格：' + str(n_minprice) + ';平均价格：' + str(ac.avg_price))
        log.info('MA60：' + str(data.loc[qt_start_time, 'MA60']) + ';MA600：' + str(data.loc[qt_start_time, 'MA600']))
        flag = 0    #控制一个循环内买入不能立即卖出

        # 进场判断
        if data.loc[qt_start_time, 'MA60'] > data.loc[qt_start_time, 'MA600'] and ac.flag4 == 0:
            is_success = ac.buy(qt_start_time, 4, 1, n_maxprice, ac.unit)
            if is_success == 1:
                flag = 1
        elif data.loc[qt_start_time, 'MA60'] < data.loc[qt_start_time, 'MA600'] and ac.flag4 == 0:
            is_success = ac.buy(qt_start_time, 4, 2, n_minprice, ac.unit)
            if is_success == 1:
                flag = 1

        if len(ac.buy_records) > 0 and flag == 0:
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
    qt_start_time = qt_start_time + timedelta(minutes=1)

    try:
        n_loc = data.loc[qt_start_time, ['Open', 'High', 'Low']]
    except:
        n_loc = None

    if qt_start_time.hour == 7 and qt_start_time.minute == 59:
        if len(ac.buy_records) > 0:
            ac.avg_price = ac.buy_records['buymoney'].sum() / ac.buy_records['buycount'].sum()
            buycount = ac.buy_records['buycount'].sum()
            rate = ((ac.all_money + ac.avg_price * buycount) - 1000000)/100000
            ac.rate_df.loc[len(ac.rate_df)] = [qt_start_time.date(), rate]
        else:
            rate = (ac.all_money - 1000000) / 100000
            ac.rate_df.loc[len(ac.rate_df)] = [qt_start_time.date(), rate]
        ac.rate_df.to_excel('rate_yield.xlsx', index=None)
        ac.sell_records.to_excel('sell_records.xlsx', index=None)

    if qt_start_time > final_date:
        if len(ac.buy_records) > 0:
            ac.avg_price = ac.buy_records['buymoney'].sum() / ac.buy_records['buycount'].sum()
            buycount = ac.buy_records['buycount'].sum()
            log.info('可用余额=' + str(ac.all_money))
            log.info('持仓=' + str(ac.avg_price) + '*' + str(buycount) + '=' + str(ac.avg_price * buycount))
            log.info('最后有这么多钱：' + str(ac.all_money + ac.avg_price * buycount))
        else:
            log.info('最后有这么多钱：' + str(ac.all_money))
        break

