import pandas as pd
from datetime import datetime, timedelta
from Account import Account
import globalConf
global log
log = globalConf.getShareLogger()

# data = pd.read_csv('BTCUSDT-1m-latest10.csv')
data = pd.read_csv('BTCUSDT-1m.csv')
data = data.loc[:, ['otime', 'Open', 'Close', 'High', 'Low', 'Volume']]
data = data.rename(columns={'otime': 'Date'})
#设置date列为索引，覆盖原来索引,这个时候索引还是 object 类型，就是字符串类型。
data.set_index('Date', inplace=True)
#将object类型转化成 DateIndex 类型，pd.DatetimeIndex 是把某一列进行转换，同时把该列的数据设置为索引 index。
data.index = pd.DatetimeIndex(data.index)
#将时间顺序升序，符合时间序列
data = data.sort_index(ascending=True)

# 计算kdj
lowList = data['Low'].rolling(9).min() #计算low值9日/分钟移动最低
lowList.fillna(value=data['Low'].expanding().min(), inplace=True)
highList = data['High'].rolling(9).max() #计算high值9日移动最高
highList.fillna(value=data['High'].expanding().max(), inplace=True)
rsv = (data.loc[:, 'Close'] - lowList) / (highList - lowList) * 100
data.loc[:, 'kdj_k'] = rsv.ewm(com=3).mean()
# data.loc[:, 'kdj_d'] = data.loc[:, 'kdj_k'].ewm(com=3).mean()
# data.loc[:, 'kdj_j'] = 3.0 * data.loc[:, 'kdj_k'] - 2.0 * data.loc[:, 'kdj_d']
# print(data)

#最开始10天行情
s_date = datetime.strptime('2021-10-01 08:00:00', '%Y-%m-%d %H:%M:%S')
e_date = datetime.strptime('2021-10-11 07:59:00', '%Y-%m-%d %H:%M:%S')
final_date = datetime.strptime('2022-10-01 07:59:00', '%Y-%m-%d %H:%M:%S')
# s_date = datetime.strptime('2022-09-15 08:00:00', '%Y-%m-%d %H:%M:%S')
# e_date = datetime.strptime('2022-09-25 07:59:00', '%Y-%m-%d %H:%M:%S')
# final_date = datetime.strptime('2022-10-05 07:59:00', '%Y-%m-%d %H:%M:%S')

ac = Account(1000000, 100000, 0.01, None, None)
max_profit = 0
qt_start_time = e_date + timedelta(minutes=1)

n_loc = data.loc[qt_start_time, ['Open', 'High', 'Low']]

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

        flag = 0
        # 进场1判断
        if n_maxprice > maxprice or n_minprice < minprice:
            if n_maxprice > maxprice and (ac.buy_type is None or ac.buy_type == 1) and ac.flag1 == 0:
                ac.buy(qt_start_time, 1, 1, maxprice, ac.unit)
                # ac.buy(qt_start_time, 1, 1, maxprice, ac.all_money) #全仓买入
                flag = 1
            elif n_minprice < minprice and (ac.buy_type is None or ac.buy_type == 2) and ac.flag1 == 0:
                ac.buy(qt_start_time, 1, 2, minprice, ac.unit)
                # ac.buy(qt_start_time, 1, 2, maxprice, ac.all_money) #全仓买入
                flag = 1

        # 进场2判断
        if n_maxprice > twohours_maxprice + twohours_gapprice or n_minprice < twohours_minprice - twohours_gapprice:
            # if n_maxprice > twohours_maxprice + twohours_gapprice and ac.buy_type is None:
            if n_maxprice > twohours_maxprice + twohours_gapprice and (ac.buy_type is None or ac.buy_type == 1) and ac.flag2 == 0:
                ac.buy(qt_start_time, 2, 1, twohours_maxprice + twohours_gapprice, ac.unit)
                # ac.buy(qt_start_time, 2, 1, twohours_maxprice + twohours_gapprice, ac.all_money)    #全仓买入
                flag = 1
            elif n_minprice < twohours_minprice - twohours_gapprice and (ac.buy_type is None or ac.buy_type == 2) and ac.flag2 == 0:
                ac.buy(qt_start_time, 2, 2, twohours_minprice - twohours_gapprice, ac.unit)
                # ac.buy(qt_start_time, 2, 2, twohours_minprice - twohours_gapprice, ac.all_money)
                flag = 1

        # 进场3判断
        if data.loc[qt_start_time, 'kdj_k'] > 75 and (ac.buy_type is None or ac.buy_type == 1) and ac.flag3 == 0:
            log.info('k值=' + str(data.loc[qt_start_time, 'kdj_k']))
            ac.buy(qt_start_time, 3, 2, n_loc['Open'], ac.unit)
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

            # 达到买入仓位的0.4%盈利，出场
            if sell_completed_flag != 1:
                if ac.buy_type == 1 or ac.buy_type == 2:
                    if ac.buy_type == 1:
                        profit = (n_maxprice-ac.avg_price)/ac.avg_price
                        price = ac.avg_price * (1 + 0.004)
                    if ac.buy_type == 2:
                        profit = (ac.avg_price-n_minprice)/ac.avg_price
                        price = ac.avg_price * (1 - 0.004)
                    if profit >= 0.004:
                        ac.sell(qt_start_time, 2, price)

            # 获利回调出场 最高后的75%出场
            # if sell_completed_flag != 1:
            #     if ac.buy_type == 1 or ac.buy_type == 2:
            #         if ac.buy_type == 1:
            #             profit = (n_maxprice-ac.avg_price)/ac.avg_price
            #         if ac.buy_type == 2:
            #             profit = (ac.avg_price-n_minprice)/ac.avg_price
            #     if max_profit < profit:
            #         max_profit = profit
            #     if max_profit > 0 and profit <= max_profit*0.75:
            #         if ac.buy_type == 1:
            #             price = ac.avg_price * (1 + max_profit * 0.75)
            #         if ac.buy_type == 2:
            #             price = ac.avg_price * (1 - max_profit * 0.75)
            #         ac.sell(qt_start_time, 2, price)
            #         max_profit = 0

            # 固定持有30分钟出场
            # if len(ac.buy_records) > 0 and qt_start_time >= ac.buy_records.loc[0]['buytime'] + timedelta(minutes=30):
            #     if ac.buy_type == 1:
            #         ac.sell(qt_start_time, 3, n_maxprice)
            #     if ac.buy_type == 2:
            #         ac.sell(qt_start_time, 3, n_minprice)

    sell_completed_flag = 0
    s_date = s_date + timedelta(minutes=1)
    e_date = e_date + timedelta(minutes=1)
    qt_start_time = e_date + timedelta(minutes=1)

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

