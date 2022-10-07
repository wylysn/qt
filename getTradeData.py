from datetime import datetime
from dateutil.relativedelta import relativedelta
import requests
import shutil
import pandas as pd
from logbook import Logger
import logbook
from zipfile import ZipFile
import time
import os

# log = Logger('getTradeData.py', level=logbook.INFO)
import globalConf
global log
log = globalConf.getShareLogger()

columns = ['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume',
           'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore']


def download_spot_klines(symbol, period, date: datetime, path):
    """
    下载现货K线历史行情数据
    :param symbol: 交易对
    :param period: 时间周期，比如：1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1mo
    :param date: 日期
    :param path: 文件保存路径
    """

    # https://data.binance.vision/data/spot/monthly/klines/ETHUSDT/1m/ETHUSDT-1m-2021-06.zip
    # url = 'https://data.binance.vision/data/spot/daily/klines/%s/%s/%s-%s-%s-%02d.zip' % (
    #     symbol, period, symbol, period, date.year, date.month)

    url = 'https://data.binance.vision/data/spot/daily/klines/%s/%s/%s-%s-%s-%02d-%02d.zip' % (
    symbol, period, symbol, period, date.year, date.month, date.day)

    print(url)
    log.info(url)

    with requests.get(url, stream=True) as r:
        with open(path, 'wb') as f:
            shutil.copyfileobj(r.raw, f)

    print(path)
    return path


def download_spot_klines_range(symbol, period, start: datetime, end: datetime, dir=''):
    """
    下载指定时间范围的币安现货K线历史行情数据
    :param symbol: 交易对
    :param period: 时间周期，比如：1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1mo
    :param start: 开始日期
    :param end: 结束日期
    :param dir: 数据存放目录
    """

    # ETHUSDT/5m/ETHUSDT-5m-2017-11.zip

    if len(dir) > 0 and not dir.endswith('/'):
        dir += '/'

    os.makedirs('%s%s/%s' % (dir, symbol, period), exist_ok=True)

    while True:

        path = '%s%s/%s/%s-%s-%s-%02d-%02d.zip' % (dir, symbol, period, symbol, period, start.year, start.month, start.day)

        download_spot_klines(symbol, period, start, path)

        # start = start + relativedelta(months=+1)
        start = start + relativedelta(days=+1)

        if start > end:
            break

        time.sleep(2)


def read_history_file(zip_file, csv_file) -> pd.DataFrame:
    """
    读取历史数据文件
    :param zip_file: zip文件路径
    :param csv_file: csv文件路径
    """
    # ETHUSDT-5m-2017-08.csv
    zf = ZipFile(zip_file)
    file = zf.open(csv_file)
    df = pd.read_csv(file, header=None, names=columns)
    file.close()
    zf.close()
    return df


def merge_history_file(dir, output) -> pd.DataFrame:
    """
    合并历史数据
    :param dir: 历史数据文件存放目录
    :param output: 合并文件输出路径
    """
    merge_df = None

    for file in os.listdir(dir):
        log.info('merge %s to %s' % (file, output))
        print('-----------')
        print(dir)
        print(file)
        df = read_history_file(dir + '/' + file, file.replace('.zip', '.csv'))

        merge_df = df if merge_df is None else pd.concat([merge_df, df])

    merge_df.to_csv(output, index=False)

    return merge_df


if __name__ == '__main__':
    # download_spot_klines_range('ETHUSDT', '1d', start=datetime(2021, 9, 27), end=datetime(2022, 8, 31))
    # merge_history_file('ETHUSDT/1d', 'ETHUSDT/ETHUSDT-1d.csv')
    download_spot_klines_range('BTCUSDT', '1m', start=datetime(2022, 9, 15), end=datetime(2022, 10, 4))
    merge_history_file('BTCUSDT/1m', 'BTCUSDT/BTCUSDT-1m-latest10.csv')


