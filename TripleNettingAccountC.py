import re

import pandas as pd
from logbook import Logger
import logbook
import globalConf
global log
log = globalConf.getShareLogger()

class TripleNettingAccountC():
    def __init__(self, all_money:float, unit=None, stop_profit=None):
        self.all_money = all_money
        self.freeze_deposit = 0
        self.unit = unit
        self.stop_profit = stop_profit
        # side: 1:买多 2:买空
        # trade_type 0:建仓or加仓；1:止损；2:获利回调;
        # trade_strategy 5:网格交易
        self.trade_records = pd.DataFrame(columns=['side', 'trade_type', 'trade_type_desc', 'trade_strategy',
                                                   'tradetime', 'tradecount', 'tradeprice', 'trademoney'])
        # self.singleloop_trade_records = pd.DataFrame(
        #     columns=['side', 'trade_type', 'trade_type_desc', 'trade_strategy', 'tradetime', 'tradecount', 'tradeprice', 'trademoney'])
        self.position = pd.DataFrame(columns=['side', 'positioncnt', 'avgprice'])

    def printinfo(self):
        print("总金额：", self.all_money)
        print("买入一个单位：", self.unit)
        print("止损点：", self.stop_profit)
        print("交易情况：", self.trade_records)
        # print("单轮交易情况：", self.singleloop_trade_records)
        print("当前持仓情况：", self.position)

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
        self.position.loc[0] = [side, position_cnt, price]
        log.info("下单情况--side:{},trade_type:{},trade_strategy:{},trade_time:{},position_cnt:{},price:{},order_money:{}".format
            (side, trade_type, trade_strategy, trade_time, position_cnt, price, order_money))
        log.info("下单持仓情况:{}".format(self.position))

    def close_oder(self, trade_time:str,trade_type:str,trade_strategy:str, side:str, price:float,all_money:float,position_cnt:int,position_all_money:float):
        log.info("平仓,现持仓情况:{}".format(self.position.loc[0]))
        self.all_money = all_money
        log.info("计算之后的总金额:{}".format(self.all_money))
        # 写到交易记录到内存
        self.trade_records.loc[len(self.trade_records)] = [side, trade_type, position_all_money, trade_strategy,
                                                           trade_time,
                                                           position_cnt, price, self.all_money]
        order_money = price * position_cnt
        log.info(
            "下单情况--side:{},trade_type:{},trade_strategy:{},trade_time:{},position_cnt:{},price:{},order_money:{}".format
            (side, trade_type, trade_strategy, trade_time, position_cnt, price, order_money))
        #删除持仓
        self.position = self.position.drop(index=self.position.index)

    def get_position(self):
        return self.position

    def write_result(self):
        log.info("最后持仓情况:{}".format(self.position))
        log.info("交易记录:{}".format(self.trade_records))
        self.trade_records.to_excel('boll_result.xlsx')