#!/usr/bin/env python 
# -*- coding: utf-8 -*-
"""
File Name ：tools.py
date ： 2022/11/22
time ： 20:03
Author ： wsy
desc ：
"""
from datetime import datetime
import time
import requests

from chinese_calendar import is_workday

def local_day():

    now = datetime.now().strftime("%Y-%m-%d")
    day = datetime.strptime(now, "%Y-%m-%d")
    return day
    # return time.strftime('%Y-%m-%d', time.localtime(time.time()))

def local_day_str():
    return time.strftime('%Y-%m-%d', time.localtime(time.time()))

def is_trading_day(day=None):
    """
    判断day是否是股票交易日
    """
    if day is None:
        day = local_day()
    # print(day)
    if is_workday(day):
        if day.weekday() == 5 or day.weekday() == 6:
            return False
        else:
            return True
    else:
        return False

def get_stock_info(code: str):
    """
    采用腾讯股票接口获取股票信息
    """
    sina_url = "http://qt.gtimg.cn/q="
    if code.startswith('6'):
        url = sina_url + "sh" + code
    if code.startswith('0'):
        url = sina_url + "sz" + code
    if code.startswith('3'):
        url = sina_url + "sz" + code
    retry_count = 1
    stock_info = {}
    while retry_count < 4:
        try:
            resp = requests.get(url=url)
            data = resp.text
            stock_info_list = data.split('~')
            # print(stock_info_list)
            stock_info['name'] = stock_info_list[1]
            stock_info['code'] = stock_info_list[2]
            stock_info['price'] = stock_info_list[3]
            stock_info['TTM'] = stock_info_list[39]
            stock_info['volume_ratio'] = stock_info_list[49]
            stock_info['turnover_rate'] = stock_info_list[38]
            stock_info['outer_disc'] = stock_info_list[7]
            stock_info['inter_disc'] = stock_info_list[8]
            stock_info['circulation_market_value'] = stock_info_list[44]
            break
        except:
            time.sleep(2)
            retry_count += 1
    return stock_info

# if __name__ == "__main__":
#     stock = get_stock_info('300750')
#     print(stock)