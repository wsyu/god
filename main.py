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

from tortoise import Tortoise

from setting import *
from tasks import add_task


async def run():
    await Tortoise.init(db_url=f"mysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}", modules={"models": ["models"]}, use_tz=False, timezone='Asia/Shanghai')
    scheduler.start()
    await add_task()


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run())
    loop.run_forever()