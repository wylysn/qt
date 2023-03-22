import pandas as pd
from datetime import datetime, time, timedelta
import globalConf
import talib

from TripleNettingAccount import TripleNettingAccount

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
# df_1d = data
# df_1d = df_1d.resample('D').agg({'Open':'first','Close':'last','High':'max','Low':'min'})
# df_1d['preClose'] = df_1d['Close'].shift(1)
# df_1d['preHigh'] = df_1d['High'].shift(1)
# df_1d['preLow'] = df_1d['Low'].shift(1)
# df_1d['upperline'] = df_1d['High'].rolling(window=20).max()
# df_1d['lowline'] = df_1d['Low'].rolling(window=20).min()
# df_1d['middleline'] = df_1d[['upperline', 'lowline']].apply(lambda x: (x['upperline'] + x['lowline']) / 2, axis=1)
#
# df_1d['TR'] = df_1d[['High', 'Low', 'Close', 'preHigh', 'preLow', 'preClose']].apply(
#     lambda x: max(x['High'] - x['Low'], x['preHigh'] - x['preClose'], x['preClose'] - x['preLow']),
#     axis=1)
# # 计算 ATR 值
# df_1d['ATR5'] = df_1d['TR'].rolling(window=5).mean()
# df_1d['ATR20'] = df_1d['TR'].rolling(window=20).mean()
# df_1d['SAR'] = talib.SAR(df_1d['High'].values, df_1d['Low'].values, acceleration=0.02)

start_date = datetime.strptime('2021-12-31 23:59:00', '%Y-%m-%d %H:%M:%S')
end_date = datetime.strptime('2022-01-21 23:58:00', '%Y-%m-%d %H:%M:%S')
final_date = datetime.strptime('2022-12-01 23:59:00', '%Y-%m-%d %H:%M:%S')

ac = TripleNettingAccount(all_money=10000)
qt_start_time = end_date + timedelta(minutes=1)

SYMBOL="ETHUSDT"
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
        perioddata = data.loc[start_date:end_date]
        df_1d = perioddata
        df_1d = df_1d.resample('D').agg({'Open': 'first', 'Close': 'last', 'High': 'max', 'Low': 'min'})
        if qt_start_time.hour == 0 and qt_start_time.minute == 0 and qt_start_time.second == 0:
            latest = [n_openprice, n_closeprice, n_maxprice, n_minprice]
        else:
            # lastest_line = df_1d.tail(1)
            n_open = df_1d.iloc[-1]['Open']
            n_close = n_closeprice
            n_high = n_maxprice
            if n_high < df_1d.iloc[-1]['High']:
                n_high = df_1d.iloc[-1]['High']
            n_low = n_minprice
            if n_low > df_1d.iloc[-1]['Low']:
                n_low = df_1d.iloc[-1]['Low']
            latest = [n_open, n_close, n_high, n_low]
        df_1d.loc[qt_start_time.strftime("%Y-%m-%d 00:00:00")] = latest
        df_1d['preClose'] = df_1d['Close'].shift(1)
        df_1d['preHigh'] = df_1d['High'].shift(1)
        df_1d['preLow'] = df_1d['Low'].shift(1)
        df_1d['upperline'] = df_1d['High'].rolling(window=20).max()
        df_1d['lowline'] = df_1d['Low'].rolling(window=20).min()
        df_1d['middleline'] = df_1d[['upperline', 'lowline']].apply(lambda x: (x['upperline'] + x['lowline']) / 2,
                                                                    axis=1)
        df_1d['TR'] = df_1d[['High', 'Low', 'Close', 'preHigh', 'preLow', 'preClose']].apply(
            lambda x: max(x['High'] - x['Low'], x['preHigh'] - x['preClose'], x['preClose'] - x['preLow']),
            axis=1)
        # 计算 ATR 值
        df_1d['ATR5'] = df_1d['TR'].rolling(window=5).mean()
        df_1d['ATR20'] = df_1d['TR'].rolling(window=20).mean()
        df_1d['SAR'] = talib.SAR(df_1d['High'].values, df_1d['Low'].values, acceleration=0.02)

        last_line = df_1d.iloc[-1]
        last_second_line = df_1d.iloc[-2]

        log.info(
            "pre_close:【{}】, upperline:【{}】, middleline:【{}】, lowline:【{}】, ATR5:【{}】, ATR20:【{}】, SAR:【{}】, current_high:【{}】, current_low:【{}】"
            .format(pre_close, last_line['upperline'], last_line['middleline'], last_line['lowline'],
                    last_line['ATR5'], last_line['ATR20'], last_line['SAR'], n_maxprice, n_minprice))
        # 卖出判断
        if len(ac.position) > 0:
            position = ac.get_position()
            position_side = position['side'].values[0]
            position_cnt = position['positioncnt'].values[0]
            position_middleline = position['middleline'].values[0]
            position_atr5 = position['atr5'].values[0]
            avgprice = position['avgprice'].values[0]
            position_all_money = avgprice * position_cnt
            gap = last_line['SAR'] - avgprice
            loss_or_profit = gap * position_cnt
            # 1.当SAR指标由多转空，多单平仓；SAR指标由空转多，空单平仓
            if ac.position.iloc[-1]['side'] == 'BUY' and n_minprice < pre_close and n_maxprice > last_line['SAR']:
                current_all_money = position_all_money + loss_or_profit
                log.info("平仓[SAR由多转空]")
                ac.close_oder(qt_start_time, SYMBOL, "平仓[SAR由多转空]", "SELL", last_line['SAR'], current_all_money,
                              position_cnt, position_all_money, last_line['middleline'], last_line['ATR5'])
                continue
            elif ac.position.iloc[-1]['side'] == 'SELL' and n_maxprice > pre_close and n_minprice < last_line['SAR']:
                current_all_money = position_all_money - loss_or_profit
                log.info("平仓[SAR由空转多]")
                ac.close_oder(qt_start_time, SYMBOL, "平仓[SAR由空转多]", "SELL", last_line['SAR'], current_all_money,
                              position_cnt, position_all_money, last_line['middleline'], last_line['ATR5'])
                continue

            #2. 当价格偏离第一层滤网中心线10个ATR
            if ac.position.iloc[-1]['side'] == 'BUY':
                if n_minprice <= position_middleline-10*position_atr5:
                    current_all_money = position_all_money + loss_or_profit
                    log.info("向下偏离中心线10个atr")
                    ac.close_oder(qt_start_time, SYMBOL, "向下偏离中心线10个atr", "SELL", position_middleline-10*position_atr5, current_all_money,
                                  position_cnt, position_all_money, last_line['middleline'], last_line['ATR5'])
                elif n_maxprice >= position_middleline+10*position_atr5:
                    current_all_money = position_all_money + loss_or_profit
                    log.info("向上偏离中心线10个atr")
                    ac.close_oder(qt_start_time, SYMBOL, "向上偏离中心线10个at", "SELL",
                                  position_middleline + 10 * position_atr5, current_all_money,
                                  position_cnt, position_all_money, last_line['middleline'], last_line['ATR5'])
            elif ac.position.iloc[-1]['side'] == 'SELL':
                if n_minprice <= position_middleline-10*position_atr5:
                    current_all_money = position_all_money - loss_or_profit
                    log.info("向下偏离中心线10个atr")
                    ac.close_oder(qt_start_time, SYMBOL, "向下偏离中心线10个atr", "BUY", position_middleline-10*position_atr5, current_all_money,
                                  position_cnt, position_all_money, last_line['middleline'], last_line['ATR5'])
                elif n_maxprice >= position_middleline+10*position_atr5:
                    current_all_money = position_all_money - loss_or_profit
                    log.info("向上偏离中心线10个atr")
                    ac.close_oder(qt_start_time, SYMBOL, "向上偏离中心线10个atr", "BUY",
                                  position_middleline + 10 * position_atr5, current_all_money,
                                  position_cnt, position_all_money, last_line['middleline'], last_line['ATR5'])

        if len(ac.position) <= 0:
            # 买入判断
            # 1.第一层滤网 （唐安奇通道平滑线）：
            # 上阻力线 =过去20天的最高价
            # 下阻力线 =过去20天的最低价
            # 中心线 二（上阻力线＋下阻力线）12
            # 当前价格向上击穿上阻力线，做多（第一层条件）
            # 当前价格向下击穿下阻力线，做空（第一层条件）
            pre_close = pre_loc['Close']
            flag1 = -1    #0：做多；1：做空
            last_line = df_1d.iloc[-1]
            if n_minprice < pre_close and n_maxprice > last_second_line['upperline']:
                flag1 = 0
                log.info('第一层滤网符合条件')
            elif n_maxprice > pre_close and n_minprice < last_second_line['lowline']:
                log.info('第一层滤网符合条件')
                flag1 = 1
            # else:
            #     continue

            # 2.第二层滤网（波幅ATR指标）
            # TR = Max(当前交易日最高价与最低价的波幅，前一个交易日24时价格 - 前一个交易日最高价，前一个交易日24时价格 - 前一个交易日最低价）
            # ATR = MA(TR, N) PS: MA为移动平均，N为天数
            # 当5天ATR小于等于20天ATR时，符合条件（在相对低位寻求下一次波动机会）
            flag2 = 0
            if last_line['ATR5'] <= last_line['ATR20']:
                log.info('第二层滤网符合条件')
                flag2 = 1
            # else:
            #     continue

            # 3.第三层滤网(SAR 抛物线指标）
            # 买入条件：当前价格从SAR曲线下方开始向上突破SAR曲线时，为做多买入信号
            # 当前价格从SAR曲线上方开始向下突破SAR曲线时，为做空买入信号
            flag3 = -1  # 0：做多；1：做空

            if n_minprice < pre_close and n_maxprice > last_line['SAR']:
                log.info('第三层滤网符合条件')
                flag3 = 0
            elif n_maxprice > pre_close and n_minprice < last_line['SAR']:
                log.info('第三层滤网符合条件')
                flag3 = 1
            # else:
            #     continue

            if flag1 == 0 and flag2 == 1 and flag3 == 0:
                log.info("做多")
                ac.order_all(qt_start_time, SYMBOL, "多头买进", "BUY", last_line['SAR'], last_line['middleline'], last_line['ATR5'])
            elif flag1 == 1 and flag2 == 1 and flag3 == 1:
                log.info("做空")
                ac.order_all(qt_start_time, SYMBOL, "空头卖出", "SELL", last_line['SAR'], last_line['middleline'], last_line['ATR5'])
            # else:
            #     continue
