#!/usr/bin/env python 
# -*- coding: utf-8 -*-
"""
File Name ：tasks.py
date ： 2022/11/22
time ： 16:52
Author ： wsy
desc ：
"""
import asyncio
import re
import time
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from playwright.async_api import async_playwright, Page
from chinese_calendar import is_workday

from tools import local_day
from setting import INTERVAL_TASK

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

async def search_stock(page:Page, search_str):
    url = "http://www.iwencai.com/unifiedwap/home/index"
    await page.goto(url)
    await page.locator("textarea[type=\"text\"]").click()
    await page.locator("textarea[type=\"text\"]").fill(search_str)
    await page.locator("//*[@id='searchInputWrap']/div[1]/div[1]/div[2]").click()
    try:
        gp_list_html = page.locator("//*[@id='iwc-table-container']/div[5]/div[2]/div[2]/div/table/tbody")
        gp_list_str = await gp_list_html.text_content()
        # 格式化股票数据
        re_str = r"\s\d+\s"
        gp_list = re.sub(pattern=re_str, repl=' ', string=gp_list_str).split(' ')[1:]
        # print(gp_list)
    except:
        gp_list = []
    return gp_list


async def search_gp(search_str: str):
    """
    按条件搜索股票
    """
    local_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    print(f"{local_time}正在筛选数据...")
    # print(search_str)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--start-maximized"])
        context = await browser.new_context(no_viewport=True)
        page =  await context.new_page()
        # 绕过机器人检测
        js = """
            Object.defineProperties(navigator, {webdriver:{get:()=>undefined}});
            """
        await page.add_init_script(js)

        a_gp_list = await search_stock(page, search_str)
        if a_gp_list:
            print(a_gp_list)
            # send_wechat(push_content)
        else:
            print("未匹配到相应数据！！！")

        await page.close()
        await context.close()
        await browser.close()

async def gp_start():
    if is_trading_day():
        today = datetime.now().strftime("%Y%m%d")
        dt_9_40 = datetime.strptime(today + ' 09:40', "%Y%m%d %H:%M")
        dt_11_30 = datetime.strptime(today + ' 11:30', "%Y%m%d %H:%M")
        dt_13_00 = datetime.strptime(today + ' 13:00', "%Y%m%d %H:%M")
        dt_14_48 = datetime.strptime(today + ' 14:48', "%Y%m%d %H:%M")
        scheduler.add_job(search_gp, 'interval', seconds=150, id='sw', args=[search_str],
                          start_date=dt_9_40, end_date=dt_11_30, replace_existing=True, timezone='Asia/Shanghai')
        scheduler.add_job(search_gp, 'interval', seconds=150, id='xw', args=[search_str],
                          start_date=dt_13_00, end_date=dt_14_48, replace_existing=True, timezone='Asia/Shanghai')
    else:
        print("今天不是交易日~~~")

async def keep_db_conn():
    print(f"当前时间：{datetime.now().strftime( '%Y-%m-%d %H:%M:%S')}")

async def add_task():
    scheduler = AsyncIOScheduler(**INTERVAL_TASK)
    scheduler.start()
    scheduler.add_job(keep_db_conn, 'interval', id='keep_db', seconds=6, timezone='Asia/Shanghai',
                      replace_existing=True)
    scheduler.add_job(gp_start, 'cron', id='push_start', hour='9', minute='00', timezone='Asia/Shanghai',
                      replace_existing=True)


    # await keep_db_conn()

# if __name__ == "__main__":
#     search_str = "上穿5日均线；上穿10日均线；股价大于20日均线；涨跌幅小于4；日rsi金叉；市盈ttm大于0；量比大于2；外盘/内盘≥1.3；股价在3到35元之间；非中字头；非科创板；非*st；非北交所；非银行股；"
#     asyncio.run(search_gp(search_str))
