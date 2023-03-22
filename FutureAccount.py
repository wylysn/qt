import re

import pandas as pd
from logbook import Logger
import logbook
import globalConf
global log
log = globalConf.getShareLogger()

class FutureAccount():
    def __init__(self, all_money:float, unit=None, stop_profit=None):
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
                n_price = (o_cnt * o_price + amount) / n_cnt
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
            if n_cnt <= 0:
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

    def order2(self, trade_time, trade_type, trade_strategy, side, price, amount, trade_type_desc):
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
                log.info('持仓数量：' + str(o_cnt) +'; 持仓均价：' + str(o_price))
                n_cnt = o_cnt + amount / price
                n_price = (o_cnt * o_price + amount) / n_cnt
                self.position.loc[0] = [initial_side, n_cnt, n_price]
            else:
                self.position.loc[0] = [initial_side, amount / price, price]
            self.all_money = self.all_money - amount
            log.info(trade_type_desc + '|' + str(side) + '|' + str(trade_strategy) + '|' + str(trade_time) + '|' + str(price) + '|' + str(
                amount / price) + '|' + str(amount))
        else:   # 减仓/止损
            o_cnt = self.position.loc[0]['positioncnt']
            o_price = self.position.loc[0]['avgprice']
            log.info('持仓数量：' + str(o_cnt) + '; 持仓均价：' + str(o_price))
            sell_cnt = amount / price
            if amount >= o_cnt * price:
                amount = o_cnt * price
                sell_cnt = o_cnt
            n_cnt = o_cnt - sell_cnt
            n_price = o_price
            self.position.loc[0] = [initial_side, n_cnt, n_price]
            if initial_side == 1:
                sell_money = amount
            elif initial_side == 2:
                if(trade_type_desc != '止损'):
                    sell_money = amount + sell_cnt * (o_price - price)
                else:
                    sell_money = amount / (1-(o_price - price) / o_price) * (1 + (o_price - price) / o_price)
                # sell_money = amount / (1-(o_price - price) / o_price) * (1 + (o_price - price) / o_price)
                # =50000/(1-(1508.359104 - 1483.205458) / 1508.359104) * (1 + (1508.359104 - 1483.205458) / 1508.359104)
            self.all_money = self.all_money + sell_money

            if n_cnt == 0 and trade_type_desc != '止损':
                trade_type_desc = '售空'
            self.trade_records.loc[len(self.trade_records)] = [side, trade_type, trade_type_desc, trade_strategy, trade_time,
                                                               sell_cnt, price, sell_money]
            self.singleloop_trade_records.loc[len(self.singleloop_trade_records)] = [side, trade_type, trade_type_desc, trade_strategy,
                                                                                     trade_time, sell_cnt, price,
                                                                                     sell_money]
            log.info(trade_type_desc + '|' + str(side) + '|' + str(trade_strategy) + '|' + str(trade_time) + '|' + str(price) + '|' + str(
                sell_cnt) + '|' + str(sell_money))

            if n_cnt == 0:
                self.singleloop_trade_records = self.singleloop_trade_records.drop(index=self.singleloop_trade_records.index)
                self.position = self.position.drop(index=self.position.index)

        return 1

    def order3(self, trade_time, trade_type, trade_strategy, side, price, amount, count, trade_type_desc):
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
                log.info('持仓数量：' + str(o_cnt) + '; 持仓均价：' + str(o_price))
                n_cnt = o_cnt + amount / price
                n_price = (o_cnt * o_price + amount) / n_cnt
                self.position.loc[0] = [initial_side, n_cnt, n_price]
            else:
                self.position.loc[0] = [initial_side, amount / price, price]
            self.all_money = self.all_money - amount
            log.info(trade_type_desc + '|' + str(side) + '|' + str(trade_strategy) + '|' + str(trade_time) + '|' + str(price) + '|' + str(
                amount / price) + '|' + str(amount))
        else:   # 减仓、止损
            o_cnt = self.position.loc[0]['positioncnt']
            o_price = self.position.loc[0]['avgprice']
            log.info('持仓数量：' + str(o_cnt) + '; 持仓均价：' + str(o_price))
            n_cnt = o_cnt - count
            if n_cnt <= 0:
                n_cnt = 0
                n_price = 0
            else:
                n_price = o_price
            self.position.loc[0] = [initial_side, n_cnt, n_price]
            if initial_side == 1:
                sell_money = price * count
            elif initial_side == 2:
                sell_money = count * o_price * (1 + (o_price - price) / o_price)
            self.all_money = self.all_money + sell_money

            if n_cnt <= 0 and trade_type_desc != '止损':
                trade_type_desc = '售空'
            self.trade_records.loc[len(self.trade_records)] = [side, trade_type, trade_type_desc, trade_strategy, trade_time,
                                                               count, price, sell_money]
            self.singleloop_trade_records.loc[len(self.singleloop_trade_records)] = [side, trade_type, trade_type_desc, trade_strategy,
                                                                                     trade_time, count, price,
                                                                                     sell_money]
            log.info(trade_type_desc + '|' + str(side) + '|' + str(trade_strategy) + '|' + str(trade_time) + '|' + str(price) + '|' + str(
                count) + '|' + str(sell_money))

            if n_cnt <= 0:
                self.singleloop_trade_records = self.singleloop_trade_records.drop(index=self.singleloop_trade_records.index)
                self.position = self.position.drop(index=self.position.index)

        return 1

    def order4(self, trade_time, trade_type, trade_strategy, side, price, count, trade_type_desc):
        if len(self.singleloop_trade_records) > 0:
            initial_side = self.singleloop_trade_records.loc[0]['side']
        else:
            initial_side = side
        position_cnt = 0
        position_price = 0
        if len(self.position) > 0:
            position_cnt = self.position.loc[0]['positioncnt']
            position_price = self.position.loc[0]['avgprice']
            log.info('持仓数量：' + str(position_cnt) + '; 持仓均价：' + str(position_price))

        if side == initial_side:    # 建仓or加仓
            if self.all_money == 0:
                log.info('余额为0，不能买入')
                return 0

            if price * count > self.all_money:
                count = self.all_money / price

            self.trade_records.loc[len(self.trade_records)] = [side, trade_type, trade_type_desc, trade_strategy, trade_time,
                                                               count, price, price * count]
            self.singleloop_trade_records.loc[len(self.singleloop_trade_records)] = [side, trade_type, trade_type_desc, trade_strategy,
                                                                                     trade_time, count, price, price * count]
            if len(self.position) > 0:
                new_position_cnt = position_cnt + count
                n_price = (position_cnt * position_price + count * price) / new_position_cnt
                self.position.loc[0] = [initial_side, new_position_cnt, n_price]
            else:
                self.position.loc[0] = [initial_side, count, price]
            self.all_money = self.all_money - count * price
            log.info(trade_type_desc + '|' + str(side) + '|' + str(trade_strategy) + '|' + str(trade_time) + '|' + str(price) + '|' + str(
                count) + '|' + str(price * count))
        else:   # 减仓、止损
            new_position_cnt = position_cnt - count
            if new_position_cnt <= 0:
                new_position_cnt = 0
                new_position_price = 0
            else:
                new_position_price = position_price
            self.position.loc[0] = [initial_side, new_position_cnt, new_position_price]
            if initial_side == 1:
                sell_money = price * count
            elif initial_side == 2:
                sell_money = count * position_price * (1 + (position_price - price) / position_price)
            self.all_money = self.all_money + sell_money

            if new_position_cnt <= 0 and trade_type_desc != '止损':
                trade_type_desc = '售空'
            self.trade_records.loc[len(self.trade_records)] = [side, trade_type, trade_type_desc, trade_strategy, trade_time,
                                                               count, price, sell_money]
            self.singleloop_trade_records.loc[len(self.singleloop_trade_records)] = [side, trade_type, trade_type_desc, trade_strategy,
                                                                                     trade_time, count, price,
                                                                                     sell_money]
            log.info(trade_type_desc + '|' + str(side) + '|' + str(trade_strategy) + '|' + str(trade_time) + '|' + str(price) + '|' + str(
                count) + '|' + str(sell_money))

            if new_position_cnt <= 0:
                self.singleloop_trade_records = self.singleloop_trade_records.drop(index=self.singleloop_trade_records.index)
                self.position = self.position.drop(index=self.position.index)

        return 1

    def order_all(self, trade_time:str,trade_type:str, trade_strategy:str, side:str, price:float):
        tmp = self.all_money / price
        position_cnt = float(str(tmp).split('.')[0] + '.' + str(tmp).split('.')[1][:3])
        log.info("tmp:{},position_cnt:{}".format(tmp,position_cnt))
        log.info("下单时总余额是:{},当前价:{},购买数量:{}".format(self.all_money,price,position_cnt))
        #钱不够
        if position_cnt < 0.001:
            log.info('余额:{},现价:{},可购买:{},放弃购买'.format(self.all_money,price,position_cnt))
            return
        #有持仓,不继续下单
        if len(self.position) > 0:
            log.info('有用持仓:{},放弃购买'.format(self.position))
            return
        order_money = price * position_cnt
        self.all_money = self.all_money - order_money
        log.info("order_money:{},余额:{}".format(order_money,self.all_money))
        #写到交易记录到内存
        self.trade_records.loc[len(self.trade_records)] = [side, trade_type, self.all_money, trade_strategy,
                                                               trade_time,
                                                               position_cnt, price, price * position_cnt]
        #刷新最新持仓
        self.position.loc[0] = [side,position_cnt, price]
        log.info("下单情况--side:{},trade_type:{},trade_strategy:{},trade_time:{},position_cnt:{},price:{},order_money:{}".format
            (side, trade_type, trade_strategy,trade_time,position_cnt, price, order_money))
        log.info("下单持仓情况:{}".format(self.position))

    def close_oder(self, trade_time:str,trade_type:str,trade_strategy:str, side:str, price:float,all_money:float,position_cnt:int,position_all_money:float):
        log.info("平仓,现持仓情况:{}".format(self.position.loc[0]))
        self.all_money = all_money
        log.info("计算之后的总金额:{}".format(self.all_money))
        # 写到交易记录到内存
        self.trade_records.loc[len(self.trade_records)] = [side, trade_type, position_all_money, trade_strategy,
                                                           trade_time,
                                                           position_cnt, price, self.all_money]
        #删除持仓
        self.position = self.position.drop(index=self.position.index)

    def get_position(self):
        return self.position

    def write_result(self):
        log.info("最后持仓情况:{}".format(self.position))
        log.info("交易记录:{}".format(self.trade_records))
        self.trade_records.to_excel('boll_result.xlsx')