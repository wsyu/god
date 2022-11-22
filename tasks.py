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
from typing import List


from playwright.async_api import async_playwright, Page

from models import Stock
from setting import scheduler
from tools import local_day_str, get_stock_info, is_trading_day


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

async def stock_save_db(stock_list: List):
    """
    股票数据存入数据库
    如果已存在并且已推送，则忽略
    如果已存在，未推送，更新价格和量比
    如果未存在，直接添加
    """
    day = local_day_str()
    for stock in stock_list:
        stock_code = stock[0:6]
        stock_name = stock[6:]
        stock_object = await Stock.filter(code=stock_code, day=day).first()
        if stock_object:
            stock_info = get_stock_info(stock_code)
            await Stock.get(code=stock_code, day=day).update(last_price=stock_info['price'],
                                                             TTM=stock_info['TTM'],
                                                             volume_ratio=stock_info['volume_ratio'],
                                                             add_num=F('add_num') + 1)
        else:
            stock_info = get_stock_info(stock_code)
            # print(stock_info)
            await Stock.create(code=stock_code, name=stock_name, day=day,
                               first_price=stock_info['price'],
                               last_price=stock_info['price'],
                               TTM=stock_info['TTM'],
                               volume_ratio=stock_info['volume_ratio'] )

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
            await stock_save_db(a_gp_list)
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
        search_str = "上穿5日均线；上穿10日均线；股价大于20日均线；涨跌幅小于4；日rsi金叉；市盈ttm大于0；量比大于2；外盘/内盘≥1.3；股价在3到35元之间；非中字头；非科创板；非*st；非北交所；非银行股；"
        scheduler.add_job(search_gp, 'interval', seconds=150, id='sw', args=[search_str],
                          start_date=dt_9_40, end_date=dt_11_30, replace_existing=True, timezone='Asia/Shanghai')
        scheduler.add_job(search_gp, 'interval', seconds=150, id='xw', args=[search_str],
                          start_date=dt_13_00, end_date=dt_14_48, replace_existing=True, timezone='Asia/Shanghai')
    else:
        print("今天不是交易日~~~")

async def keep_db_conn():
    print(f"当前时间：{datetime.now().strftime( '%Y-%m-%d %H:%M:%S')}")

async def add_task():

    scheduler.add_job(keep_db_conn, 'interval', id='keep_db', seconds=60*60*4, timezone='Asia/Shanghai',
                      replace_existing=True)
    scheduler.add_job(gp_start, 'cron', id='push_start', hour='9', minute='00', timezone='Asia/Shanghai',
                      replace_existing=True)


    # await keep_db_conn()

# if __name__ == "__main__":
#     search_str = "上穿5日均线；上穿10日均线；股价大于20日均线；涨跌幅小于4；日rsi金叉；市盈ttm大于0；量比大于2；外盘/内盘≥1.3；股价在3到35元之间；非中字头；非科创板；非*st；非北交所；非银行股；"
#     asyncio.run(search_gp(search_str))
