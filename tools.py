#!/usr/bin/env python 
# -*- coding: utf-8 -*-
"""
File Name ：tools.py
date ： 2022/11/22
time ： 20:03
Author ： wsy
desc ：
"""
import datetime
import time

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