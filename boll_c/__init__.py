import pandas as pd
from datetime import datetime, timedelta
import globalConf
import talib

from FutureAccount import FutureAccount

global log
log = globalConf.getShareLogger()

#均线11天,15天,30天
#boll轨道参数11天,boll(上轨),boll(中轨),bool(下轨)
data = pd.read_csv('./../ETHUSDT/ETHUSDT-1m-20230220_time.csv')
data = data.loc[:, ['Open time', 'Open', 'Close', 'High', 'Low', 'Volume']]
#设置date列为索引，覆盖原来索引,这个时候索引还是 object 类型，就是字符串类型。
data.set_index('Open time', inplace=True)
#将object类型转化成 DateIndex 类型，pd.DatetimeIndex 是把某一列进行转换，同时把该列的数据设置为索引 index。
data.index = pd.DatetimeIndex(data.index)
#将时间顺序升序，符合时间序列
data = data.sort_index(ascending=True)

# 中轨线=N日的移动平均线
# 上轨线=中轨线＋两倍的标准差
# 下轨线=中轨线－两倍的标准差
# n=11 对应ma89, 布林乘数3
data['upperband'], data['middleband'], data['lowerband'] = talib.BBANDS(data['Close'], timeperiod=89*60, nbdevup=1, nbdevdn=1, matype=0)
data['ma5'] = talib.MA(data['Close'], timeperiod=5*60,matype=0)
# data['ma11'] = talib.MA(data['Close'], timeperiod=660,matype=0)
# data['ma15'] = talib.MA(data['Close'], timeperiod=900,matype=0)
# data['ma30'] = talib.MA(data['Close'], timeperiod=1800,matype=0)
#删除NaN的行
# data.dropna(inplace=True)
# data.to_excel('boll_ma5.xlsx')

# data_minutes = pd.read_csv('./../ETHUSDT/ETHUSDT-1m.csv')
# data_minutes = data_minutes.loc[:, ['Date','Open time', 'Open', 'Close', 'High', 'Low', 'Volume']]
# data_minutes.set_index('Open time', inplace=True)
# #将object类型转化成 DateIndex 类型，pd.DatetimeIndex 是把某一列进行转换，同时把该列的数据设置为索引 index。
# data_minutes.index = pd.DatetimeIndex(data_minutes.index)
# #将时间顺序升序，符合时间序列
# data_minutes = data_minutes.sort_index(ascending=True)
# data_minutes.to_excel('data_minutes.xlsx')

start_date = datetime.strptime('2023-02-21 08:00:00', '%Y-%m-%d %H:%M:%S')
final_date = datetime.strptime('2023-03-02 23:59:00', '%Y-%m-%d %H:%M:%S')

ac = FutureAccount(all_money=1000)
qt_start_time = start_date
SYMBOL="ETHUSDT"
current_close = 0
pre_close = 0
while True:
    log.info('--------------------------------')
    log.info('当前时间:{}'.format(qt_start_time))
    try:
        # day_loc = data.loc[str(qt_start_time), ['ma5','ma11', 'ma15', 'ma30', 'upperband', 'middleband', 'lowerband']]
        # minute_loc1 = data[data['Open time'] == str(qt_start_time)]
        # log.info(minute_loc)
        # minute_loc = data.loc[qt_start_time, ['ma5','ma11', 'ma15', 'ma30', 'upperband', 'middleband', 'lowerband']]
        # minute_loc = data.loc[qt_start_time, ['ma5', 'upperband', 'middleband', 'lowerband']]
        minute_loc = data.loc[qt_start_time, ['Open', 'Close','ma5', 'upperband', 'middleband', 'lowerband']]
    except Exception as e:
        log.error(e)
        log.info("Key:{} 不存在,捕获异常".format(qt_start_time))
        break
        # day_loc = None
    if minute_loc is not None:
        ma5 = minute_loc['ma5']
        # ma11 = minute_loc['ma11']
        # ma15 = minute_loc['ma15']
        # ma30 = minute_loc['ma30']
        upperband = minute_loc['upperband']
        middleband = minute_loc['middleband']
        lowerband = minute_loc['lowerband']
        # log.info('ma11:{},ma15:{},ma30:{},upperband:{},middleband:{},lowerband:{}'.format(ma11,ma15,ma30,upperband,middleband,lowerband))
        #A版
        # 条件：  MA15>Ma30，当前价突破上轨线，空头买进   平仓:当前价下穿boll下轨
        # 条件：  MA15<Ma30，当前价突破下轨线，多头买进   平仓:当前价上穿boll上轨
        # for循环1天1440分钟线,整个时间复杂度n²。即：天数*分钟

        # log.info("赋值前,pre_close:{},current_close:{}".format(pre_close,current_close))
        # open_time = minute[0]
        close = minute_loc['Close']
        if pre_close == 0:
            pre_close = close
        if current_close != 0:
            pre_close = current_close
        current_close = close

        position = ac.get_position()
        # 平仓判断
        if len(position.values) > 0:
            # 多头买进 平仓: 当前价上穿boll上轨
            position_side = position['side'].values[0]
            position_cnt = position['positioncnt'].values[0]
            avgprice = position['avgprice'].values[0]
            position_all_money = avgprice * position_cnt
            gap = current_close - avgprice
            loss_or_profit = abs(gap) * position_cnt
            stop_rate = 0.10
            # b版,止损、止盈 买入成本1%
            max_profit = position_all_money * 0.01
            if position_side == 'BUY' and pre_close > middleband and middleband > current_close:
                log.info(
                    "pre_close:【{}】,middleband:【{}】,current_close:【{}】"
                    .format(pre_close, middleband, current_close))
                if gap > 0:
                    current_all_money = position_all_money + loss_or_profit
                else:
                    current_all_money = position_all_money - loss_or_profit
                log.info(
                    "open_time:【{}】,平仓[当前跌破中轨],SELL,current_close:【{}】,current_all_money:【{}】,position_cnt:【{}】,position_all_money:【{}】"
                    .format(qt_start_time, current_close, current_all_money, position_cnt, position_all_money))
                ac.close_oder(qt_start_time, SYMBOL, "平仓[当前跌破中轨]", "SELL", current_close, current_all_money,
                              position_cnt, position_all_money)
                # continue

        if pre_close < ma5 and ma5 < current_close and current_close > upperband:
            log.info("pre_close:【{}】,ma5:【{}】,current_close:【{}】,upperband:【{}】"
                     .format(pre_close, ma5, current_close, upperband))
            log.info("多头买进")
            ac.order_all(qt_start_time, SYMBOL, "多头买进", "BUY", current_close)
    else:
        log.info("取不到数据,循环结束")
        break
    qt_start_time = qt_start_time + timedelta(minutes=1)
ac.write_result()
