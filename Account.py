import pandas as pd
from logbook import Logger
import logbook
import globalConf
global log
log = globalConf.getShareLogger()

class Account():
    def __init__(self, all_money, unit, stop_profit, buy_type, create_type):
        self.all_money = all_money
        self.unit = unit
        self.stop_profit = stop_profit
        self.buy_type = None    # 1:做多；2:做空
        self.sell_type = None  # 1:止损；2:获利回调; 3:30分钟固定卖出；
        self.create_type = None  # 1:进场条件1；2：进场条件2 3：进场条件3 4: MA60判断进场
        self.flag1 = 0  # 条件1进场标识 0：未进场； 1：已进场
        self.flag2 = 0  # 条件2进场标识 0：未进场； 1：已进场
        self.flag3 = 0  # 条件3进场标识 0：未进场； 1：已进场
        self.flag4 = 0  # MA60进场标识 0：未进场； 1：已进场
        self.flag5 = 0  # 网格策略进场标识 0：未进场； 1：已进场
        self.buy_records = pd.DataFrame(columns=['buytime', 'buycount', 'buyprice', 'buymoney'])
        self.avg_price = None
        self.rate_df = pd.DataFrame(columns=['closetime', 'allmoney'])

        self.sell_records = pd.DataFrame(columns=['selltime', 'sellcount', 'sellprice', 'avgprice', 'profit'])
        self.remaining = 0

    def printinfo(self):
        print("总金额：", self.all_money)
        print("买入一个单位：", self.unit)
        print("止损点：", self.stop_profit)
        print("买入类型：", self.buy_type)
        print("进场类型：", self.create_type)
        print("交易情况：", self.buy_records)

    def buy(self, trade_time, create_type, buy_type, price, amount):
        self.create_type = create_type
        if self.create_type == 1:
            self.flag1 = 1
        elif self.create_type == 2:
            self.flag2 = 1
        elif self.create_type == 3:
            self.flag3 = 1
        elif self.create_type == 4:
            self.flag4 = 1
        elif self.create_type == 5:
            self.flag4 = 5

        self.buy_type = buy_type
        # if self.all_money >= amount:
        #     self.all_money = self.all_money - amount
        #     self.buy_records.loc[len(self.buy_records)] = [trade_time, amount/price, price, amount]
        #     log.info('买入' + '|' + str(self.create_type) + '|' + str(self.buy_type) + '|' + str(trade_time) + '|' + str(price) + '|' + str(amount/price) + '|' + str(amount))
        # else:
        #     log.info('余额不足，余额为：' + self.all_money)
        if self.all_money >= amount:
            self.all_money = self.all_money - amount
            self.buy_records.loc[len(self.buy_records)] = [trade_time, amount/price, price, amount]
            is_success = 1
            self.remaining = self.remaining + amount/price
            log.info('买入' + '|' + str(self.create_type) + '|' + str(self.buy_type) + '|' + str(trade_time) + '|' + str(price) + '|' + str(amount/price) + '|' + str(amount))
        elif 0 < self.all_money < amount:
            # log.info('余额不足，余额为：' + self.all_money)
            self.buy_records.loc[len(self.buy_records)] = [trade_time, self.all_money / price, price, self.all_money]
            is_success = 1
            self.remaining = self.remaining + self.all_money / price
            log.info(
                '买入' + '|' + str(self.create_type) + '|' + str(self.buy_type) + '|' + str(trade_time) + '|' + str(
                    price) + '|' + str(self.all_money / price) + '|' + str(self.all_money))
            self.all_money = 0
        else:
            is_success = 0

        return is_success

    def sell(self, trade_time, sell_type, price):
        self.sell_type = sell_type
        sellcount = self.buy_records['buycount'].sum()
        log.info('buy_type:' + str(self.buy_type))
        log.info('price:' + str(price))
        log.info('avgprice:' + str(self.avg_price))
        log.info('sellcount:' + str(sellcount))
        if self.buy_type == 1:
            sellmoney = price * sellcount
        elif self.buy_type == 2:
            sellmoney = self.avg_price * sellcount * (1 - (price - self.avg_price) / price)
        self.all_money = self.all_money + sellmoney
        self.buy_records = self.buy_records.drop(index=self.buy_records.index)
        self.create_type = None
        self.buy_type = None
        self.flag1 = 0
        self.flag2 = 0
        self.flag3 = 0
        self.flag4 = 0
        self.flag5 = 0
        self.remaining = 0
        log.info('卖出' + '|' + str(sell_type) + '|' + str(trade_time) + '|' + str(price) + '|' + str(sellcount) + '|' + str(sellmoney))
        origin_buymoney = self.avg_price * sellcount
        profit = sellmoney - origin_buymoney
        log.info('盈利:' + str(profit))
        self.sell_records.loc[len(self.sell_records)] = [trade_time, sellcount, price, self.avg_price, profit]

    # def sellwithgrid(self, trade_time, sell_type, price, amount):
    #     self.sell_type = sell_type
    #     log.info('buy_type:' + str(self.buy_type))
    #     log.info('price:' + str(price))
    #     log.info('sellcount:' + str(amount))
    #     if self.buy_type == 1:
    #         sellmoney = price * amount
    #     elif self.buy_type == 2:
    #         sellmoney = price * amount * (1 - (price - self.avg_price) / price)
    #     self.all_money = self.all_money + sellmoney
    #     self.buy_records = self.buy_records.drop(index=self.buy_records.index)
    #     self.create_type = None
    #     self.buy_type = None
    #     self.flag1 = 0
    #     self.flag2 = 0
    #     self.flag3 = 0
    #     self.flag4 = 0
    #     self.flag5 = 0
    #     log.info('卖出' + '|' + str(sell_type) + '|' + str(trade_time) + '|' + str(price) + '|' + str(sellcount) + '|' + str(sellmoney))
    #     origin_buymoney = self.avg_price * sellcount
    #     profit = sellmoney - origin_buymoney
    #     log.info('盈利:' + str(profit))
    #     self.sell_records.loc[len(self.sell_records)] = [trade_time, sellcount, price, self.avg_price, profit]