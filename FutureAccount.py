import pandas as pd
from logbook import Logger
import logbook
import globalConf
global log
log = globalConf.getShareLogger()

class FutureAccount():
    def __init__(self, all_money, unit, stop_profit):
        self.all_money = all_money
        self.freeze_deposit = 0
        self.unit = unit
        self.stop_profit = stop_profit
        # side: 1:买多 2:买空
        # trade_type 0:建仓or加仓；1:止损；2:获利回调;
        # trade_strategy 5:网格交易
        self.trade_records = pd.DataFrame(columns=['side', 'trade_type', 'trade_type_desc', 'trade_strategy', 'tradetime', 'tradecount', 'tradeprice', 'trademoney'])
        self.singleloop_trade_records = pd.DataFrame(
            columns=['side', 'trade_type', 'trade_type_desc', 'trade_strategy', 'tradetime', 'tradecount', 'tradeprice', 'trademoney'])
        self.position = pd.DataFrame(columns=['side', 'positioncnt', 'avgprice'])

    def printinfo(self):
        print("总金额：", self.all_money)
        print("买入一个单位：", self.unit)
        print("止损点：", self.stop_profit)
        print("交易情况：", self.trade_records)
        print("单轮交易情况：", self.singleloop_trade_records)
        print("当前持仓情况：", self.position)

    def order(self, trade_time, trade_type, trade_strategy, side, price, amount, count, trade_type_desc):
        if len(self.singleloop_trade_records) > 0:
            initial_side = self.singleloop_trade_records.loc[0]['side']
        else:
            initial_side = side

        if side == initial_side:    # 建仓or加仓
            if 0 < self.all_money < amount:
                amount = self.all_money
            elif self.all_money == 0:
                log.info('余额为0，不能买入')
                return 0

            self.trade_records.loc[len(self.trade_records)] = [side, trade_type, trade_type_desc, trade_strategy, trade_time,
                                                               amount / price, price, amount]
            self.singleloop_trade_records.loc[len(self.singleloop_trade_records)] = [side, trade_type, trade_type_desc, trade_strategy,
                                                                                     trade_time, amount / price, price,
                                                                                     amount]
            if len(self.position) > 0:
                o_cnt = self.position.loc[0]['positioncnt']
                o_price = self.position.loc[0]['avgprice']
                n_cnt = o_cnt + amount / price
                n_price = (o_cnt * o_price + n_cnt * price) / (o_cnt + n_cnt)
                self.position.loc[0] = [initial_side, n_cnt, n_price]
            else:
                self.position.loc[0] = [initial_side, amount / price, price]
            self.all_money = self.all_money - amount
            log.info(trade_type_desc + '|' + str(side) + '|' + str(trade_strategy) + '|' + str(trade_time) + '|' + str(price) + '|' + str(
                amount / price) + '|' + str(amount))
        else:   # 减仓
            o_cnt = self.position.loc[0]['positioncnt']
            o_price = self.position.loc[0]['avgprice']
            n_cnt = o_cnt - count
            if n_cnt == 0:
                n_price = 0
            else:
                n_price = o_price
            self.position.loc[0] = [initial_side, n_cnt, n_price]
            if initial_side == 1:
                sell_money = price * count
            elif initial_side == 2:
                sell_money = count * o_price * (1 + (o_price - price) / o_price)
            self.all_money = self.all_money + sell_money
            self.trade_records.loc[len(self.trade_records)] = [side, trade_type, trade_type_desc, trade_strategy, trade_time,
                                                               count, price, sell_money]
            self.singleloop_trade_records.loc[len(self.singleloop_trade_records)] = [side, trade_type, trade_type_desc, trade_strategy,
                                                                                     trade_time, count, price,
                                                                                     sell_money]
            log.info(trade_type_desc + '|' + str(side) + '|' + str(trade_strategy) + '|' + str(trade_time) + '|' + str(price) + '|' + str(
                count) + '|' + str(sell_money))

            if n_cnt == 0:
                self.singleloop_trade_records = self.singleloop_trade_records.drop(index=self.singleloop_trade_records.index)
                self.position = self.position.drop(index=self.position.index)

        return 1
