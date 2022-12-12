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

import requests
from playwright.async_api import async_playwright, Page
from tortoise.expressions import F

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
        try:
            if stock_object:
                stock_info = get_stock_info(stock_code)
                await Stock.filter(code=stock_code, day=day).update(last_price=stock_info['price'],
                                                                    TTM=stock_info['TTM'],
                                                                    volume_ratio=stock_info['volume_ratio'],
                                                                    add_num=F('add_num') + 1,
                                                                    outer_disc=stock_info['outer_disc'],
                                                                    inter_disc=stock_info['inter_disc'],
                                                                    turnover_rate=stock_info['turnover_rate'],
                                                                    circulation_market_value=stock_info[
                                                                        'circulation_market_value'],
                                                                    )
            else:

                stock_info = get_stock_info(stock_code)

                await Stock.create(code=stock_code,
                                   name=stock_name,
                                   day=day,
                                   first_price=stock_info['price'],
                                   last_price=stock_info['price'],
                                   TTM=stock_info['TTM'],
                                   volume_ratio=stock_info['volume_ratio'],
                                   outer_disc=stock_info['outer_disc'],
                                   inter_disc=stock_info['inter_disc'],
                                   turnover_rate=stock_info['turnover_rate'],
                                   circulation_market_value=stock_info['circulation_market_value'],
                                   )
        except:
            continue

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


def send_wechat(push_content):
    if push_content:
        url = "http://www.pushplus.plus/send"
        token = "fd9f40c87ee04647bd6eee375781b8e2"
        send_data = {
            "token": token,
            "title": "财富密码",
            "content": push_content,
            # "topic": "wealth",
            "template": 'html'
            }
        retry_count = 1
        while retry_count < 4:
            try:
                resp = requests.post(url=url, json=send_data)
                if resp.status_code != 200:
                    print("微信消息发送失败")
                    print(resp.text)
                    retry_count += 1
                else:
                    print("已推送到微信...")
                    break
            except:
                print("微信推送错误...")
                retry_count += 1
    else:
        print("内容为空,未推送...")

async def push_wechat():
    """
    将股票数据推送到微信
    排除已推送的
    推荐量比大于7的,次数大于2的
    """
    day = local_day_str()
    stock_list = await Stock.filter(day=day).filter(volume_ratio__gte=7, add_num__gt=2).exclude(is_push=1)
    if stock_list:
        push_content = ""
        for stock in stock_list:
            push_content += f"<p>{stock.code} {stock.name} {stock.last_price}</p>"
        send_wechat(push_content)
        await Stock.filter(day=day).filter(volume_ratio__gte=7, add_num__gt=2).update(is_push=1)


async def gp_start():
    print("股票任务开始...")
    # search_str = "上穿5日均线；上穿10日均线；股价大于20日均线；涨跌幅小于4；日rsi金叉；市盈ttm大于0；量比大于2.7；外盘/内盘≥1.3；股价在3到35元之间；非中字头；非科创板；非*st；非北交所；非银行股；"
    # search_str = '上穿5日均线；上穿10日均线；股价大于20日均线；涨跌幅小于4；市盈ttm大于0；量比大于2；外盘/内盘≥1.3；股价在3到35元之间；非中字头；非科创板；非*st；非北交所；非银行股；'
    sw_search_str = '上穿5日均线；上穿10日均线；股价大于20日均线；涨跌幅小于4；市盈ttm大于0；股价在3到35元之间；非中字头；非科创板；非*st；非北交所；非银行股；资金流入的；换手率大于上一交易日换手率的0.8倍以上；主力增仓占比>=5%；'
    xw_search_str = '上穿5日均线；上穿10日均线；股价大于20日均线；涨跌幅小于4；市盈ttm大于0；股价在3到35元之间；非中字头；非科创板；非*st；非北交所；非银行股；资金流入的；换手率大于上一交易日换手率的1.2倍以上；主力增仓占比>=5%；'
    # scheduler.add_job(search_gp, 'interval', seconds=20, id='test', args=[search_str],
    #                   replace_existing=True, timezone='Asia/Shanghai')
    if is_trading_day():
        today = datetime.now().strftime("%Y%m%d")
        dt_9_38 = datetime.strptime(today + ' 09:38', "%Y%m%d %H:%M")
        dt_11_30 = datetime.strptime(today + ' 11:30', "%Y%m%d %H:%M")
        dt_13_00 = datetime.strptime(today + ' 13:00', "%Y%m%d %H:%M")
        dt_14_48 = datetime.strptime(today + ' 14:48', "%Y%m%d %H:%M")
        scheduler.add_job(search_gp, 'interval', seconds=150, id='sw', args=[sw_search_str],
                          start_date=dt_9_38, end_date=dt_11_30, replace_existing=True, timezone='Asia/Shanghai')
        scheduler.add_job(search_gp, 'interval', seconds=150, id='xw', args=[xw_search_str],
                          start_date=dt_13_00, end_date=dt_14_48, replace_existing=True, timezone='Asia/Shanghai')
        scheduler.add_job(push_wechat, 'interval', seconds=120, id='auto_push_wechat', start_date=dt_9_38,
                          end_date=dt_14_48, replace_existing=True, timezone='Asia/Shanghai')
    else:
        print("今天不是交易日~~~")

async def keep_db_conn():
    print(f"当前时间：{datetime.now().strftime( '%Y-%m-%d %H:%M:%S')}, 服务正常...")

async def add_task():
    print("正在启动定时任务...")
    scheduler.add_job(keep_db_conn, 'interval', id='keep_db', seconds=60*60, timezone='Asia/Shanghai',
                      replace_existing=True)
    scheduler.add_job(gp_start, 'cron', id='push_start', hour='9', minute='00', timezone='Asia/Shanghai',
                      replace_existing=True)
    # scheduler.add_job(gp_start, 'interval', id='push_start', seconds=30, timezone='Asia/Shanghai',
    #                   replace_existing=True)


    # await keep_db_conn()

# if __name__ == "__main__":
#     search_str = "上穿5日均线；上穿10日均线；股价大于20日均线；涨跌幅小于4；日rsi金叉；市盈ttm大于0；量比大于2；外盘/内盘≥1.3；股价在3到35元之间；非中字头；非科创板；非*st；非北交所；非银行股；"
#     asyncio.run(search_gp(search_str))
