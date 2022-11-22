#!/usr/bin/env python 
# -*- coding: utf-8 -*-
"""
File Name ：main.py
date ： 2022/11/22
time ： 16:04
Author ： wsy
desc ：
"""
import asyncio

from tortoise import Tortoise, run_async
from models import Stock
from setting import *

from tasks import add_task




async def run():
    await Tortoise.init(db_url=f"mysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}", modules={"models": ["models"]})
    search_str = "上穿5日均线；上穿10日均线；股价大于20日均线；涨跌幅小于4；日rsi金叉；市盈ttm大于0；量比大于2；外盘/内盘≥1.3；股价在3到35元之间；非中字头；非科创板；非*st；非北交所；非银行股；"
    await add_task()
    print(await Stock.all().values("id", "name"))


if __name__ == "__main__":
    # run_async(run())
    # asyncio.run(run())
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run())
    loop.run_forever()