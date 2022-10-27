import pandas as pd
from datetime import datetime, timedelta
from FutureAccount import FutureAccount
from logbook import Logger
import logbook
import globalConf
global log
log = globalConf.getShareLogger()

data = pd.read_csv('/Users/wangyilu/PycharmProjects/qt/ETHUSDT/ETHUSDT-1m-202110-202210.csv')
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

#最开始12小时行情
start_date = datetime.strptime('2022-07-17 00:00:00', '%Y-%m-%d %H:%M:%S')
end_date = datetime.strptime('2022-07-17 07:59:00', '%Y-%m-%d %H:%M:%S')
final_date = datetime.strptime('2022-10-17 07:59:00', '%Y-%m-%d %H:%M:%S')

ac = FutureAccount(1000000, 50000, 0.058)
trade_count_unit = 20
max_profit = 0
qt_start_time = end_date + timedelta(minutes=1)

n_loc = data.loc[qt_start_time, ['Open', 'High', 'Low']]
add_unit = 10
price_times = 1.5
empty_unit = 30

while True:
    log.info('--------------------------------')
    log.info('当前时间：' + str(qt_start_time))

    if n_loc is not None:
        perioddata = data.loc[start_date:end_date]    #入场1数据集（12小时数据）
        # 求前10天平均价
        maxdf = perioddata.mean()
        maxprice = maxdf['Close']
        log.info('前8小时平均价格：' + str(maxprice))
        # 求最大值、最小值
        # maxdf = perioddata.max()
        # maxprice = maxdf['High']
        # log.info('前12小时最高价格：' + str(maxprice))

        n_maxprice = n_loc['High']
        n_minprice = n_loc['Low']
        n_openprice = n_loc['Open']
        n_avgprice = (n_maxprice+n_minprice)/2
        log.info('当前最高价格：' + str(n_maxprice) + ';最低价格：' + str(n_minprice) + ';平均价格：' + str(n_avgprice))

        flag = 0    # 控制一个循环内买入不能立即卖出
        # 进场1判断
        if n_avgprice > maxprice+40 and len(ac.position) < 1:
            log.info('建仓')
            trade_price = maxprice+40
            if trade_price < n_openprice:
                log.info('平均价+40<开盘价，使用开盘价作为交易价')
                trade_price = n_openprice
            ac.order4(qt_start_time, 0, 5, 2, maxprice + 40, trade_count_unit, '建仓')
            flag = 1

        if len(ac.position) > 0 and flag == 0:
            avg_price = ac.position.loc[0]['avgprice']

            # 止损：损失跌破总体仓位成本的比例
            stop_price = avg_price * (1 + ac.stop_profit)
            if n_avgprice >= stop_price:
                log.info('止损')
                ac.order4(qt_start_time, 1, 5, 1, stop_price, ac.position.loc[0]['positioncnt'], '止损')
                flag = 1
            else:
                last_tradeprice_out = None
                initial_side = None
                init_tradeprice = None
                last_tradeprice_in = None
                initial_side = ac.singleloop_trade_records.loc[0]['side']
                init_tradeprice = ac.singleloop_trade_records.loc[0]['tradeprice']
                if initial_side == 1:
                    inverse_side = 2
                elif initial_side == 2:
                    inverse_side = 1

                if len(ac.singleloop_trade_records.loc[ac.singleloop_trade_records['side'] == inverse_side]) > 0:
                    last_tradeprice_out = ac.singleloop_trade_records.loc[ac.singleloop_trade_records['side'] == inverse_side].tail(1).iloc[
                        0]['tradeprice']

                if last_tradeprice_out == None:
                    last_tradeprice_out = init_tradeprice
                    log.info('最后一次减仓价格：' + str(last_tradeprice_out))

                if n_avgprice <= init_tradeprice - 30:
                    ac.order4(qt_start_time, 2, 5, 1, (init_tradeprice - 30), ac.position.loc[0]['positioncnt'],
                             '平仓')
                elif n_avgprice <= init_tradeprice - 20 and init_tradeprice == last_tradeprice_out:
                    ac.order4(qt_start_time, 2, 5, 1, (init_tradeprice - 20), ac.position.loc[0]['positioncnt']/2,
                             '首次减仓')

        initial_side = None
        init_tradeprice = None
        last_tradeprice_in = None
        if len(ac.singleloop_trade_records) > 0 and flag == 0:
            initial_side = ac.singleloop_trade_records.loc[0]['side']
            init_tradeprice = ac.singleloop_trade_records.loc[0]['tradeprice']
            last_tradeprice_in = ac.singleloop_trade_records.loc[ac.singleloop_trade_records['side'] == initial_side].tail(1).iloc[0]['tradeprice']
            add_position_count = len(ac.singleloop_trade_records.loc[ac.singleloop_trade_records['side'] == initial_side])
            log.info('A1基准价：' + str(init_tradeprice))
            log.info('最后一次加仓价格：' + str(last_tradeprice_in))
            last_tradeprice_out = None
            if initial_side == 1:
                inverse_side = 2
            elif initial_side == 2:
                inverse_side = 1
            # 以初始买入价格A1为基准，价格每上涨1.5倍网格度就买空1个单位
            will_buy_price = init_tradeprice + add_unit * (1.5 ** add_position_count)
            if n_avgprice >= will_buy_price and len(ac.position) > 0:
                log.info('加仓')
                ac.order4(qt_start_time, 0, 5, 2, will_buy_price, trade_count_unit,
                         '加仓')
                # avg_price = ac.position.loc[0]['avgprice']
                # log.info('avgprice=' + str(avg_price))


    start_date = start_date + timedelta(minutes=1)
    end_date = end_date + timedelta(minutes=1)
    qt_start_time = qt_start_time + timedelta(minutes=1)

    try:
        n_loc = data.loc[qt_start_time, ['Open', 'High', 'Low']]
    except:
        n_loc = None

    if qt_start_time > final_date:
        if len(ac.position) > 0:
            avg_price = ac.position.loc[0]['avgprice']
            positioncnt = ac.position.loc[0]['positioncnt']
            log.info('可用余额=' + str(ac.all_money))
            if ac.position.loc[0]['side'] == 1:
                log.info('持仓=' + str(avg_price) + '*' + str(positioncnt) + '=' + str(avg_price * positioncnt))
                log.info('最后有这么多钱：' + str(ac.all_money + avg_price * positioncnt))
            else:
                postion_actual_money = positioncnt * avg_price * (1 + (avg_price - n_avgprice) / avg_price)
                log.info('持仓=' + str(positioncnt) + '*' + str(avg_price) + '*' + '(1+(' + str(avg_price) + '-' + str(n_avgprice) + '）/' + str(avg_price) + ')=' + str(postion_actual_money))
                log.info('最后有这么多钱：' + str(ac.all_money + postion_actual_money))
        else:
            log.info('最后有这么多钱：' + str(ac.all_money))

        ac.trade_records.to_excel('trade_records.xlsx', index=None)
        break