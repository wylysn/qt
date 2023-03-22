import pandas as pd
from datetime import datetime, time, timedelta
import globalConf
import talib as ta

from TripleNettingAccountC import TripleNettingAccountC

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

start_date = datetime.strptime('2021-12-31 23:59:00', '%Y-%m-%d %H:%M:%S')
end_date = datetime.strptime('2022-01-20 23:58:00', '%Y-%m-%d %H:%M:%S')
final_date = datetime.strptime('2022-12-01 23:59:00', '%Y-%m-%d %H:%M:%S')

ac = TripleNettingAccountC(10000)
qt_start_time = end_date + timedelta(minutes=1)

SYMBOL = "ETHUSDT"
atr_leverage = 1
current_close = 0
pre_close = 0
while True:
    start_date = start_date + timedelta(minutes=1)
    end_date = end_date + timedelta(minutes=1)
    qt_start_time = qt_start_time + timedelta(minutes=1)
    log.info('--------------------------------')
    log.info('当前时间:{}'.format(qt_start_time))
    try:
        n_loc = data.loc[qt_start_time, ['Open', 'Close', 'High', 'Low']]
    except:
        # 统计
        ac.trade_records.to_excel('trade_records.xlsx', index=None)
        break
    pre_loc = data.loc[end_date, ['Open', 'Close', 'High', 'Low']]
    n_maxprice = n_loc['High']
    n_minprice = n_loc['Low']
    n_openprice = n_loc['Open']
    n_closeprice = n_loc['Close']
    # log.info('当前最高价格：' + str(n_maxprice) + ';最低价格：' + str(n_minprice) + ';open price：' + str(n_openprice))

    if n_loc is not None:
        period_df = data.loc[start_date:end_date]
        hourly_df = period_df
        hourly_df = hourly_df.resample('H').agg({'Open': 'first', 'Close': 'last', 'High': 'max', 'Low': 'min'})
        if qt_start_time.hour == 0 and qt_start_time.minute == 0 and qt_start_time.second == 0:
            latest = [n_openprice, n_closeprice, n_maxprice, n_minprice]
        else:
            # lastest_line = df_1h.tail(1)
            n_open = hourly_df.iloc[-1]['Open']
            n_close = n_closeprice
            n_high = n_maxprice
            if n_high < hourly_df.iloc[-1]['High']:
                n_high = hourly_df.iloc[-1]['High']
            n_low = n_minprice
            if n_low > hourly_df.iloc[-1]['Low']:
                n_low = hourly_df.iloc[-1]['Low']
            latest = [n_open, n_close, n_high, n_low]
        hourly_df.loc[qt_start_time] = latest

        daily_df = hourly_df.resample('D').agg({'Open': 'first', 'Close': 'last', 'High': 'max', 'Low': 'min'})
        daily_df['preClose'] = daily_df['Close'].shift(1)
        daily_df['preHigh'] = daily_df['High'].shift(1)
        daily_df['preLow'] = daily_df['Low'].shift(1)
        daily_df['TR'] = daily_df[['High', 'Low', 'Close', 'preHigh', 'preLow', 'preClose']].apply(
            lambda x: max(x['High'] - x['Low'], x['preHigh'] - x['preClose'], x['preClose'] - x['preLow']),
            axis=1)
        daily_df['ATR'] = daily_df['TR'].rolling(window=10).mean()
        daily_df['middle'] = daily_df['Close'].ewm(span=20, min_periods=20).mean()
        hourly_df.loc[:, 'upperline'] = None
        hourly_df.loc[:, 'lowline'] = None
        hourly_df.loc[:, 'ATR'] = None
        hourly_df.loc[hourly_df.index[-1], 'middle'] = daily_df.iloc[-1]['middle']
        hourly_df.loc[hourly_df.index[-1], 'ATR'] = daily_df.iloc[-1]['ATR']
        hourly_df.loc[hourly_df.index[-1], 'upperline'] = hourly_df.iloc[-1]['middle'] + atr_leverage * hourly_df.iloc[-1]['ATR']
        hourly_df.loc[hourly_df.index[-1], 'lowline'] = hourly_df.iloc[-1]['middle'] - atr_leverage * hourly_df.iloc[-1]['ATR']

        last_line = hourly_df.iloc[-1]
        # last_second_line = hourly_df.iloc[-2]
        #
        # if hourly_df.index[-2].day == hourly_df.index[-1].day:
        #     hourly_df.loc[hourly_df.index[-2], 'upperline'] = hourly_df.iloc[-1]['middle'] + atr_leverage * daily_df.iloc[-1]['ATR']
        #     hourly_df.loc[hourly_df.index[-2], 'lowline'] = hourly_df.iloc[-1]['middle'] - atr_leverage * daily_df.iloc[-1]['ATR']
        #     hourly_df.loc[hourly_df.index[-2], 'ATR'] = daily_df.iloc[-1]['ATR']
        #     hourly_df.loc[hourly_df.index[-1], 'middle'] = daily_df.iloc[-1]['middle']
        # else:
        #     hourly_df.loc[hourly_df.index[-2], 'upperline'] = hourly_df.iloc[-2]['middle'] + atr_leverage * daily_df.iloc[-2][
        #         'ATR']
        #     hourly_df.loc[hourly_df.index[-2], 'lowline'] = hourly_df.iloc[-2]['middle'] - atr_leverage * daily_df.iloc[-2]['ATR']
        #     hourly_df.loc[hourly_df.index[-2], 'ATR'] = daily_df.iloc[-2]['ATR']

        # 计算RSI指标
        hourly_df['rsi'] = ta.RSI(hourly_df['Close'], timeperiod=14)

        # 计算KDJ指标
        hourly_df['slowk'], hourly_df['slowd'] = ta.STOCH(hourly_df['High'], hourly_df['Low'], hourly_df['Close'])
        last_line = hourly_df.iloc[-1]
        last_second_line = hourly_df.iloc[-2]
        log.info(
            "pre_close:【{}】, upperline:【{}】, middleline:【{}】, lowline:【{}】, ATR:【{}】, current_high:【{}】, current_low:【{}】"
            .format(pre_close, last_line['upperline'], last_line['middle'], last_line['lowline'],
                    last_line['ATR'],  n_maxprice, n_minprice))
        # 卖出判断
        if len(ac.position) > 0:
            position = ac.get_position()
            position_side = position['side'].values[0]
            position_cnt = position['positioncnt'].values[0]
            avgprice = position['avgprice'].values[0]
            position_all_money = avgprice * position_cnt
            gap = last_line['middle'] - avgprice
            loss_or_profit = gap * position_cnt
            # 1.当前价格低于中轨线，多单卖出
            if ac.position.iloc[-1]['side'] == 'BUY' and n_maxprice >= last_line['middle'] and n_minprice < last_line['middle']:
                current_all_money = position_all_money + loss_or_profit
                log.info("平仓[价格低于中轨线]")
                ac.close_oder(qt_start_time, SYMBOL, "平仓[价格低于中轨线]", "SELL", last_line['middle'], current_all_money,
                              position_cnt, position_all_money)
                continue
            # 2.当前价格高于中轨线，空单卖出
            elif ac.position.iloc[-1]['side'] == 'SELL' and n_minprice <= last_line['middle'] and n_maxprice > last_line['middle']:
                current_all_money = position_all_money - loss_or_profit
                log.info("平仓[当前价格高于中轨线]")
                ac.close_oder(qt_start_time, SYMBOL, "平仓[当前价格高于中轨线]", "SELL", last_line['middle'], current_all_money,
                              position_cnt, position_all_money)
                continue

        if len(ac.position) <= 0:
            buy_price = 0

            # 第一层滤网（肯特纳通道）
            # 中轨=动态四小时平均线=（前四小时的最高价＋前四小时的最低价＋前四小时的close价格） /3
            # 上轨 =中轨+2*ATR
            # 下轨 =中轨-2*ATR
            # 备注：ATR = MA(TR,N) PS:MA为移动平均，N为天数，取N=1
            # 当前价格由下向上击上轨线，做多
            # （第一层条件）
            # 当前价格由上向下击穿下轨线，做空
            # （第一层条件）
            pre_close = pre_loc['Close']
            flag1 = -1    #0：做多；1：做空
            if n_minprice <= last_line['upperline'] and n_maxprice > last_line['upperline']:
                buy_price = last_line['upperline']
                flag1 = 0
                log.info('第一层滤网符合条件')
            elif n_maxprice >= last_line['lowline'] and n_minprice < last_line['lowline']:
                buy_price = last_line['lowline']
                log.info('第一层滤网符合条件')
                flag1 = 1
            # else:
            #     continue

            # 第二层滤网 (RSI波动指标）
            # 小时线的RSI不大于80时，做多（第二层条件）
            # 小时线的RS不小于20时，做空（第二层条件）
            flag2 = -1   #0：做多；1：做空
            if last_line['rsi'] <= 80:
                log.info('第二层滤网符合条件')
                flag2 = 0
            elif last_line['rsi'] >= 20:
                log.info('第二层滤网符合条件')
                flag2 = 1
            # else:
            #     continue

            # 第三层滤网(KDJ指标）
            # 小时线的KDJ指标，K值不大于80时，做多（第三层条件）
            # 小时线的KD)指标，K值不小于20时，做空 （第三层条件）
            flag3 = -1  # 0：做多；1：做空
            if last_line['slowk'] <= 80:
                log.info('第三层滤网符合条件')
                flag3 = 0
            elif last_line['slowk'] >= 20:
                log.info('第三层滤网符合条件')
                flag3 = 1
            # else:
            #     continue

            if flag1 == 0 and flag2 == 0 and flag3 == 0:
                log.info("做多")
                ac.order_all(qt_start_time, SYMBOL, "多头买进", "BUY", buy_price)
            elif flag1 == 1 and flag2 == 1 and flag3 == 1:
                log.info("做空")
                ac.order_all(qt_start_time, SYMBOL, "空头卖出", "SELL", buy_price)
            # else:
            #     continue

